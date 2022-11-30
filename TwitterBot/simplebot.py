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

LANGUAGE = get_env_variable("LANGUAGE")

print("=====> starting simple bot - Language : " + LANGUAGE)


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
    if LANGUAGE == 'en':
        team1_t = match['home_name']
        team2_t = match['away_name']
    else:
        team1_t = translations[match['home_name']]['translation'][LANGUAGE]
        team2_t = translations[match['away_name']]['translation'][LANGUAGE]
    
    hashtag = "#"+translations[match['home_name']]['hashtag']+translations[match['away_name']]['hashtag']
    dict = {"team_1": team1_t, "team_2": team2_t,
             "hashtag": hashtag,
               "location": match["location"], "elapsed": match["time"], "death_minute": death_minute,
             "death_match": death_match, "death_stadium": death_stadium, "death_cumulated": death_cumulated, "score": match["score"]}

    randommsg = random.choice(list_tweets[event])
    nonformmsg = randommsg["message"]
    message = nonformmsg.format(**dict)
    print(message)

    