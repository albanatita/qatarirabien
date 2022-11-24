# messageServer

## About The Project

The purpose of the app is to read the current status of football matches with the LiveScoreAPI, to extract the interesting data, transform them in a message and broadcast the message to the clients, especially the twitterbot and the web server.
The core of the app is a Flask server with connexion routes:
/  ->  html page: used from a navigator to display a web page about the project
/stream -> sse messages: used by the bots and the web page to get messages when there is an important event in the match
/checkLiveScoreAPI : a request there will trigger a call on the LiveScoreAPI, processing of data and broadcast messages to listeners

The Flask works in background
a simple shell command will send a request every minute on the /checkLiveScoreAPI to update the live data

The advantage of the architecture is its flexibility and scalability: bots can be developed separately and external programs could also access the messages the server send.

### Built with
Flask, Redis, SSE, PostgreSQL

## Getting Started
This is still a development version that requires some effort to put at work. Very soon the flask server will dockerized and integrated with Traefik and PostgreSQL container to make deployment and management easier.

On Debian 10:
- all required packages installed
- app pulled from github
Set environment:
- python -m venv venv
- source ./venv/bin/activate
- modify setcredentials.sh with required data for apis and database access
- in project: source setcredentials.sh
Creation of PostGresql container : TO REPLACE WITH NEW DATABASE
- sudo docker pull postgres:latest
- sudo docker volume create postgres-volume
- sudo docker run -d --name=postgres13 -p 5432:5432 -v postgres-volume:/var/lib/postgresql/data -e POSTGRES_PASSWORD=xxxxx postgres
Creation of Redis container (for SSE messaging):
- docker run --name=redis-devel --publish=6379:6379 --hostname=redis --restart=on-failure --detach redis:latest
- flask --app messenger run --host=xxxxxxx

## Usage
start a client with SSE connexion on alkemata.com:5000/stream
See example of twitter boatd
the webpage is accessible on http://alkemata.com:5000  (caution: still instable no production server right now, only for testing purposes)

## Contributing
The most important function is in livescoreapi.py: it is extractData(events).
It contains the results from LiveScoreAPI call.
This is where the whole logic between the data processing and the creation of message is done. All other stuff are only pipes to transfer the messages.

Important is templates.py which contains templates for the message to be sent to the listeners (like twitter bots)

The present logic of the message is the following:
at each call of the live api:
- we look only at the matches which are running
- if they are not yet in the database, we add them
- if they are: we check if there is a modification in the score with respect the last record in the database. if not, we do nothing, we don't need to record it. If there is a new score, we record it in the database and we add the elapsed time to the total accumulated time which is used for comparison with the number of victims. we broadcats a message to the listeners like the bot.