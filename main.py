#IPL BOT
#Code Credits: https://github.com/rohandesai-028/pollbot

#Libraries
import numpy as np
import pandas as pd
from datetime import datetime, time, date
#Telegram APIs from python-telegram-bot package
#https://python-telegram-bot.readthedocs.io/en/stable/
from telegram.ext import Updater, PollHandler
from telegram.ext import CommandHandler
from telegram.ext import PollAnswerHandler

# -----------------------------
#User Config Section
# -----------------------------
#Global Config variables

ipl_schedule_path = 'ipl_schedule.csv'
poll_data_path = 'poll_info.csv'

#Telegram API Token
#Talk to @BotFather to create your BOT and generate access tocken
#https://core.telegram.org/bots#6-botfather

API_TOKEN = #Enter your Telegram bot Token here


# -----------------------------
# Implementation
# NOTE! Do not edit code beyond this point unless you know what you are doing
# -----------------------------

df = pd.read_csv(ipl_schedule_path)
poll_survey_log = pd.read_csv(poll_data_path)
API = API_TOKEN

updater = Updater(token=API, use_context=True)
dispatcher = updater.dispatcher


def process_question(schedule_today):
    global df
    a = schedule_today
    index = a.index
    a.reset_index(drop=True, inplace=True)
    poll_q = ''
    poll_o = ''
    if len(a) == 1:
        print('poll flag = ', a['Poll Flag'][0])
        if int(datetime.now().time().hour) == 19:
            if a['Poll Flag'][0] == 0:
                poll_q = str(a['Team']).split()[1] + ' vs ' + str(a['Team2']).split()[1]
                poll_o = [str(a['Team']).split()[1], str(a['Team2']).split()[1]]
                df.at[index[0], 'Poll Flag'] = 1
                df.to_csv(ipl_schedule_path, index=False)
                df = pd.read_csv(ipl_schedule_path)
                return False, poll_q, poll_o
            else:
                return True, poll_q, poll_o
        else:
            return True, poll_q, poll_o
    else:
        if int(datetime.now().time().hour) == 15:
            if a['Poll Flag'][0] == 0:
                print("in 3-4pm")
                a = a.drop([1], axis=0)
                poll_q = str(a['Team']).split()[1] + ' vs ' + str(a['Team2']).split()[1]
                poll_o = [str(a['Team']).split()[1], str(a['Team2']).split()[1]]
                df.at[index[0], 'Poll Flag'] = 1
                df.to_csv(ipl_schedule_path, index=False)
                df = pd.read_csv(ipl_schedule_path)
            else:
                return True, poll_q, poll_o
        elif int(datetime.now().time().hour) == 19:
            if a['Poll Flag'][1] == 0:
                print("in 7-8pm")
                a = a.drop([0], axis=0)
                print(a)
                poll_q = str(a['Team']).split()[1] + ' vs ' + str(a['Team2']).split()[1]
                poll_o = [str(a['Team']).split()[1], str(a['Team2']).split()[1]]
                df.at[index[0], 'Poll Flag'] = 1
                df.to_csv(ipl_schedule_path, index=False)
                df = pd.read_csv(ipl_schedule_path)
            else:
                return True, poll_q, poll_o
        else:
            return True, poll_q, poll_o
    return False, poll_q, poll_o


def stats_processing(update, context):
    poll_survey_log = pd.read_csv(poll_data_path)
    print("poll_survey log \n", poll_survey_log.head())
    unique_voters = poll_survey_log['Name'].unique()
    points_point = []
    for i in range(0, len(unique_voters)):
        poll_survey_voter = poll_survey_log[poll_survey_log['Name'] == unique_voters[i]]
        predicted_list = np.where(poll_survey_voter["Voter Choice"] == poll_survey_voter["Prediction Result"], 1, 0)
        points = sum(predicted_list)
        points_point.append(points)
    leader = {unique_voters[i]: points_point[i] for i in range(len(points_point))}
    leader = dict(sorted(leader.items(), key=lambda x: x[1], reverse=True))
    leader_string = "Leaderboards\n```\n"
    for key, value in leader.items():
        leader_string = leader_string + "{0:<20} {1}".format(key, value) + "\n"
    leader_string = leader_string + "```"
    print(leader_string)
    context.bot.send_message(chat_id=update.effective_chat.id, text=leader_string, parse_mode='Markdown')
    pass


def start(update, context):
    df = pd.read_csv(ipl_schedule_path)
    date_today = str(date.today())
    schedule_today = df.loc[df['Date'] == date_today]
    b = schedule_today
    print(schedule_today)
    invalid_time, poll_question, poll_option = process_question(schedule_today)
    if invalid_time:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Not yet time for Predictions!!!")
    else:
        context.bot.send_poll(chat_id=update.effective_chat.id, question=poll_question, options=poll_option,
                              is_anonymous=0, open_period=600)
        b['Poll Flag'][0] = 1



def receive_poll_answer(update, context):
    global df, poll_survey_log
    answer = update.poll_answer
    poll_id = answer.poll_id
    name = answer.user.first_name
    option_chosen = answer.option_ids
    new_voter = {'Poll ID': poll_id, 'Name': name, 'Question': '', 'Voter Choice': option_chosen[0],
                 'Prediction Result': 2}
    poll_survey_log.loc[len(poll_survey_log.index)] = new_voter
    poll_survey_log.to_csv(poll_data_path, index=False)


def image_process(update, context):
    context.bot.send_photo(chat_id=update.effective_chat.id, photo='https://pbs.twimg.com/media/DcIUwRYWsAMz4Ak.jpg')


def help(update, context):
    help_info = '''IPL Fantasy League 

This bot starts a prediction poll 30 mins prior to match start time

Following are the supported commands
/start - starts the IPL Bot
/predict - to send your match prediction
/stats - to view leaderboard

Note
1. You can only vote once and cannot change your prediction
2. Voting will be disabled 10 min after prediction poll starts
3. Stats will be updated 30 min after match ends'''
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_info)


start_handler = CommandHandler('predict', start)
dispatcher.add_handler(start_handler)

dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))

stats_handler = CommandHandler('stats', stats_processing)
dispatcher.add_handler(stats_handler)

image_handler = CommandHandler('start', image_process)
dispatcher.add_handler(image_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

updater.start_polling()
