# IPL-Prediction-Poll-Bot
A simple Telegram Bot for IPL Fantasy Prediction. 

This is a fun little bot for IPL messaging groups. Users can predict the winner of the upcoming IPL match, 30 minutes before the start of the match. 
Someone has to manually update the results of the match by setting the Poll flag in the CSV based on the outcome of the match.  

List of All the usable commands:
1. /start
2. /prediction
3. /stats

Procedure to start the poll
1. Use the /start command to initiate the bot. 
2. Use the /prediction command to start accepting predictions.  
The Poll question is displayed as Team 1 vs Team 2.  
If Team 1 wins, then no need to edit the flag. If Team 2 wins, the flag must be manually set to 1. 
3. The results of the prediction are stored in a separate csv. Users can check the leaderboard with the /stats command.
#ESCN
