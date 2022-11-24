## About The Project

The purpose of the twitterbot is to listen to the messageserver and to transfer the messages to twitter.
Not yet included is the possibility to convert text in image and add it to the message (see createImage.py)

### Built with
Tweepy, cairossvg

## Getting Started
This is still a development version that requires some effort to put at work. 

On Debian 10:
- all required packages installed
- app pulled from github
Set environment:
- python -m venv venv
- source ./venv/bin/activate
- in project: source setcredentials.sh

check that the message server is running.

## Usage
- python3 twitterbot.py

## Contributing
The code is rather simple. The possibility to add images can be added and filtering on the type of message (goals, start or end of match, language)