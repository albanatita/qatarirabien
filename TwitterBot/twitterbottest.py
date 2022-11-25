import tweepy
import json
import sseclient
import os
import requests
import time
import sys
import pickle
import random
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

# Setup access to API

#auth = tweepy.OAuthHandler(
#            CONSUMER_KEY,
#            CONSUMER_SECRET
#            )
#auth.set_access_token(
#            ACCESS_TOKEN,
#            ACCESS_SECRET
#            )
#api = tweepy.API(auth)

# media = api.media_upload("./data/img5.png")
#print(media)
# media_id = '1594982252651454466'
# post_result = api.update_status(status='Le spectacle de la desolation va reprendre sous peu', media_ids=[media_id])


# auth = tweepy.AppAuthHandler('2Z5z8ZYKMwE0OHJqSapLEvPHg','fcsYoZXN5Q8NSAu7u5KlYr5P4EOdAFcVQOLldFzOGBpeGFvUNO')
# ',expansions=['attachments.media_keys']).json()
# print(tweet)
# media1='1594319138545360897'
# client2.create_tweet(text='test camera...',media_ids=[media1])

# sys.exit()
with open("./data/tweets.csv", "r") as filestream:
    list_tweets = dict()
    for line in filestream:
        currentline = line.split(";")
        if currentline[0] not in list_tweets:
            list_tweets[currentline[0]]=[{"message": currentline[1], "picture": currentline[2]}]
        else:
            list_tweets[currentline[0]].append({"message": currentline[1], "picture": currentline[2]})
translations=pickle.load( open( "./data/translation.p", "rb" ) )

def with_requests(url, headers):
    """Get a streaming response for the given event feed using requests."""
    return requests.get(url, stream=True, headers=headers)

# api = connect_to_twitter_OAuth()


url = 'http://web:5000/stream'
# headers = {'Accept': 'text/event-stream'}
# response = with_requests(url, headers)
match=json.loads('{"away_translations":{"ja":"\u30a4\u30e9\u30f3\u30fb\u30a4\u30b9\u30e9\u30e0\u5171\u548c\u56fd","sv":"Iran","bg":"\u0418\u0440\u0430\u043d","et":"Iraan","ko":"\uc774\ub780","ar":"\u0625\u064a\u0631\u0627\u0646","fi":"Iran","es":"Ir\u00e1n","da":"Iran","de":"Iran","ka":"\u10d8\u10e0\u10d0\u10dc\u10d8","pl":"Iran","hr":"Iran","el":"\u0399\u03c1\u03ac\u03bd","nl":"Iran","lt":"Iranas","fr":"Iran","vi":"Iran","it":"Iran","sr":"\u0418\u0440\u0430\u043d","no":"Iran","pt":"Ir\u00e3o","ro":"Iran","fa":"\u0627\u06cc\u0631\u0627\u0646","sk":"Ir\u00e1n","th":"\u0e2d\u0e34\u0e2b\u0e23\u0e48\u0e32\u0e19","hu":"Ir\u00e1n","zh":"\u4f0a\u6717","tr":"\u0130ran","cs":"\u00cdr\u00e1n","ru":"\u0418\u0440\u0430\u043d"},"away_id":1436,"home_id":1456,"location":"Khalifa International Stadium, Al Rayyan","home_name":"England","date":"2022-11-21","group_id":1914,"time":"13:00:00","league_id":0,"odds":{"pre":{"2":null,"1":null,"X":null},"live":{"2":null,"1":null,"X":null}},"round":"1","home_translations":{"ja":"\u30a4\u30ae\u30ea\u30b9","sv":"Storbritannien","bg":"\u0412\u0435\u043b\u0438\u043a\u043e\u0431\u0440\u0438\u0442\u0430\u043d\u0438\u044f","et":"Suurbritannia","ko":"\uc601\uad6d","ar":"\u0627\u0644\u0645\u0645\u0644\u0643\u0629 \u0627\u0644\u0645\u062a\u062d\u062f\u0629","fi":"Yhdistynyt kuningaskunta","es":"England","da":"Storbritannien","de":"Vereinigtes K\u00f6nigreich","ka":"\u10d8\u10dc\u10d2\u10da\u10d8\u10e1\u10d8","pl":"Wielka Brytania","hr":"Engleska","el":"\u0397\u03bd\u03c9\u03bc\u03ad\u03bd\u03bf \u0392\u03b1\u03c3\u03af\u03bb\u03b5\u03b9\u03bf","nl":"Verenigd Koninkrijk","lt":"Jungtin\u0117 Karalyst\u0117","fr":"Royaume-Uni","vi":"Anh","it":"Regno Unito","sr":"\u0415\u043d\u0433\u043b\u0435\u0441\u043a\u0430","no":"Storbritannia","pt":"Reino Unido","ro":"Regatul Unit","fa":"\u0627\u0646\u06af\u0644\u0633\u062a\u0627\u0646","sk":"Spojen\u00e9 kr\u00e1\u013eovstvo","th":"\u0e2a\u0e2b\u0e23\u0e32\u0e0a\u0e2d\u0e32\u0e13\u0e32\u0e08\u0e31\u0e01\u0e23","hu":"Egyes\u00fclt Kir\u00e1lys\u00e1g","zh":"\u82f1\u56fd","tr":"\u0130ngiltere","cs":"Spojen\u00e9 kr\u00e1lovstv\u00ed Velk\u00e9 Brit\u00e1nie a Severn\u00edho Irska","ru":"\u0412\u0435\u043b\u0438\u043a\u043e\u0431\u0440\u0438\u0442\u0430\u043d\u0438\u044f"},"id":1527779,"away_name":"Iran","competition":{"id":362,"name":"FIFA World Cup"},"competition_id":362,"league":{"id":null,"name":null,"country_id":null},"h2h":"https:\/\/livescore-api.com\/api-client\/teams\/head2head.json?key=aeR1vWoVF6VEBNo7&secret=9phC80f4DdhuuoVEDMF8I43obZ3MMrTV&team1_id=1456&team2_id=1436"}')
#client = sseclient.SSEClient(url)

event = "beforematch30"
death_stadium = 813
death_match = 102
death_minute = match["time"]
death_cumulated = 100
match['score']='3-3'
match_title = match['home_name'] + ' - ' + match['away_name']
message = ""
hashtag="#"+translations[match['home_name']]['hashtag']+translations[match['away_name']]['hashtag']
print(hashtag)
dict = {"team_1": translations[match['home_name']]['translation']['fr'], "team_2": translations[match['away_name']]['translation']['fr'],
             "hashtag": hashtag,
               "location": match["location"], "elapsed": match["time"], "death_minute": death_minute,
             "death_match": death_match, "death_stadium": death_stadium, "death_cumulated": death_cumulated, "score": match["score"]}
nonformmsg=random.choice(list_tweets[event])["message"]
message = nonformmsg.format(**dict)
print(message)
#print(list_tweets[event]["picture"].strip())