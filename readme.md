## About Qatarirabien

Qatarirabien is the software running behind the Twitter accounts @qatartonrouge and @qataredcard. The purpose is follow in live the events of a football game in the WC2022 and to send corresponding messages to Twitter with an enlightning comparison of the number of dead workers with the game event. See [Qatartonrouge, the website](https://qataredcard.eu).

The app is built in two more or less separated parts, which are spinned on together with docker-compose:

- the messageServer which pulls data from the LiveScoreAPI, transform them in data and broadcast them in messages thanks to the SSE protocol
- the Twitterbot that listens to the messages, format them according to the language and send them to twitter. It is basically an SSE client.

It is to be noted that other bots can be quickly developed based on the structure of the Twitterbot.

Please refer to the README in each subdirectory.