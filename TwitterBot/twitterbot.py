import tweepy
import json
import sseclient
import os
import requests
import time
import sys
import pickle
from dotenv import load_dotenv

language = 'fr'
print("=====> starting twitter bot")


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)


load_dotenv()
# Variables that contains the credentials to access Twitter API
ACCESS_TOKEN = get_env_variable("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = get_env_variable("TWITTER_ACCESS_SECRET")
CONSUMER_KEY = get_env_variable("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = get_env_variable("TWITTER_CONSUMER_SECRET")
BEARER_TOKEN = get_env_variable("TWITTER_BEARER_TOKEN")


auth = tweepy.OAuthHandler(
            CONSUMER_KEY,
            CONSUMER_SECRET
            )
auth.set_access_token(
            ACCESS_TOKEN,
            ACCESS_SECRET
            )
api = tweepy.API(auth)
# Setup access to API

# auth = tweepy.AppAuthHandler('2Z5z8ZYKMwE0OHJqSapLEvPHg','fcsYoZXN5Q8NSAu7u5KlYr5P4EOdAFcVQOLldFzOGBpeGFvUNO')
# client2 = tweepy.Client("AAAAAAAAAAAAAAAAAAAAAEcojgEAAAAA1kEatB2HeU2o4R0ifcEaO7EoFn0%3DQVXvU3tOI736uP1NXf2TneM7og7w6Fl7pKJSbDES2q85cUsvVw",
#                         consumer_key='eGitM8YBVPn4l2j4AoUfEvHHW', 
#                         consumer_secret='STiLyYzpl5m0wQOzvmZTSo7fIYUlW2lJRhwpTzpOmywWQRBKEG', 
#                        access_token='1593363088073424896-IJSVdFoHKPOjusKP2DjqPEutoDkdCh', 
#                        access_token_secret='dQL85vYMlBgVfzBSjx9CnSZhpoAJHSQIdGYy9nG0MHVJB',
#                        return_type = requests.Response,
#                         wait_on_rate_limit=True)

# tweet = client2.get_tweet(id='1594319140562808835',expansions=['attachments.media_keys']).json()
# print(tweet)
# media1='1594319138545360897'
# client2.create_tweet(text='test camera...',media_ids=[media1])

# sys.exit()
with open("./data/tweets.csv", "r") as filestream:
    list_tweets = dict()
    for line in filestream:
        currentline = line.split(";")
        list_tweets[currentline[0]] = {
            "message": currentline[1], "picture": currentline[2]}

translations = pickle.load( open( "./data/translation.p", "rb" ) )


def with_requests(url, headers):
    """Get a streaming response for the given event feed using requests."""
    return requests.get(url, stream=True, headers=headers)

# api = connect_to_twitter_OAuth()


url = 'http://web:5000/stream'
# headers = {'Accept': 'text/event-stream'}
# response = with_requests(url, headers)
client = sseclient.SSEClient(url)
for event in client:
    result = json.loads(event.data)
    match = result['match']
    event = result['event']
    death_stadium = 813
    death_match = 102
    death_minute = match["time"]
    death_cumulated = int(result["cumulated_time"] * 1.13)

    match_title = match['home_name'] + ' - ' + match['away_name']
    message = ""
    hashtag = "#"+translations[match['home_name']]['hashtag']+translations[match['away_name']]['hashtag']
    dict = {"team_1": translations[match['home_name']]['translation']['fr'], "team_2": translations[match['away_name']]['translation']['fr'],
             "hashtag": hashtag,
               "location": match["location"], "elapsed": match["time"], "death_minute": death_minute,
             "death_match": death_match, "death_stadium": death_stadium, "death_cumulated": death_cumulated, "score": match["score"]}
    message = list_tweets[event]["message"].format(**dict)
    if message != "":
        if list_tweets[event]["picture"] != '':
            print(message)
            try:
                media = api.media_upload("./data/"+list_tweets[event]["picture"].strip())
                api.update_status(status=message[:255], media_ids=[media.media_id])
            except Exception as e:
                print(e)
                api.update_status(status=message[:255])
        else:
            print(message)
            try:
                api.update_status(status=message[:255])
            except Exception as e:
                print(e)
        time.sleep(30)
