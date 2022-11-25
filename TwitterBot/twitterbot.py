import tweepy
import json
import sseclient
import os
import requests
import time
import sys
import random
import pickle
from dotenv import load_dotenv



def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)


#load_dotenv()
# Variables that contains the credentials to access Twitter API
ACCESS_TOKEN = get_env_variable("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = get_env_variable("TWITTER_ACCESS_SECRET")
CONSUMER_KEY = get_env_variable("TWITTER_CONSUMER_KEY")
CONSUMER_SECRET = get_env_variable("TWITTER_CONSUMER_SECRET")
BEARER_TOKEN = get_env_variable("TWITTER_BEARER_TOKEN")
LANGUAGE = get_env_variable("LANGUAGE")
API_VERSION = get_env_variable("API_VERSION")

print("=====> starting twitter bot - Language : " + LANGUAGE)

if API_VERSION == "1":
    auth = tweepy.OAuthHandler(
            CONSUMER_KEY,
            CONSUMER_SECRET
            )
    auth.set_access_token(
            ACCESS_TOKEN,
            ACCESS_SECRET
            )
    api = tweepy.API(auth)
else:
    client2=tweepy.Client(BEARER_TOKEN,consumer_key=CONSUMER_KEY,consumer_secret=CONSUMER_SECRET,
                access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET,
                return_type = requests.Response,
                         wait_on_rate_limit=True)

with open("./data/tweets_" + LANGUAGE + ".csv", "r") as filestream:
    list_tweets = dict()
    for line in filestream:
        currentline = line.split(";")
        if currentline[0] not in list_tweets:
            list_tweets[currentline[0]]=[{"message": currentline[1], "picture": currentline[2]}]
        else:
            list_tweets[currentline[0]].append({"message": currentline[1], "picture": currentline[2]})

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
    nonformmsg = ""
    hashtag = "#"+translations[match['home_name']]['hashtag']+translations[match['away_name']]['hashtag']
    dict = {"team_1": translations[match['home_name']]['translation'][LANGUAGE], "team_2": translations[match['away_name']]['translation'][LANGUAGE],
             "hashtag": hashtag,
               "location": match["location"], "elapsed": match["time"], "death_minute": death_minute,
             "death_match": death_match, "death_stadium": death_stadium, "death_cumulated": death_cumulated, "score": match["score"]}

    nonformmsg=random.choice(list_tweets[event])["message"]
    message = nonformmsg.format(**dict)
    print(message)

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
