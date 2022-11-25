from flask import Flask, render_template
from flask_sse import sse
from .tools import get_env_variable
from dotenv import load_dotenv
from datetime import timedelta, datetime
import pickle
from .models import db
from apscheduler.schedulers.background import BackgroundScheduler
from .livescoreapi import FixtureAPICall, LiveAPICall, EventAPICall
from . import models

load_dotenv()
app = Flask(__name__)
app.logger.debug('start initialization + ' + str(datetime.now()))
app.config["REDIS_URL"] = get_env_variable("REDIS_URL")
POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PASSWORD")
POSTGRES_DB = get_env_variable("POSTGRES_DB")
website_sse_url = get_env_variable("website_sse_url")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql+psycopg2://{user}:{pw}@{url}:5432/{db}'.format(
        user=POSTGRES_USER, pw=POSTGRES_PW, url=POSTGRES_URL, db=POSTGRES_DB))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(sse, url_prefix='/stream')


print("---- Initializing DB and scheduler")
db.init_app(app)
scheduler = BackgroundScheduler()


def messageDuringMatch30(fixture,cumulated_time):
    with app.app_context():
        fixture['score']=""
        msg = {'event': 'duringmatch30', 'match': fixture, "cumulated_time": cumulated_time}
        app.logger.debug("send message :" + str(msg))
        sse.publish(msg, type=msg['event'])


def messageBeforeMatch30(fixture):
    with app.app_context():
        fixture['score']=""
        msg = {'event': 'beforematch30', 'match': fixture, "cumulated_time": 0}
        app.logger.debug("send message :" + str(msg))
        sse.publish(msg, type=msg['event'])


def messageBeforeMatch10(fixture):
    with app.app_context():
        fixture['score']=""
        msg = {'event': 'beforematch10', 'match': fixture, "cumulated_time": 0}
        app.logger.debug("send message :" + str(msg))
        sse.publish(msg, type=msg['event'])


def extractData(events):
    matches_toupdate = []
    list_messages = []
    last_row = models.lastRow()
    if last_row is None:
        cumulated_time = 0
    else:
        cumulated_time = last_row.cumulatedTime
# TODO add control in case of API readding error
    for match in events['data']['match']:
        id = match['id']

        last_changed = datetime.strptime(
            match['last_changed'], '%Y-%m-%d %H:%M:%S')

        status = match['status']
        score = match['score']
        event = match['events']
        lastRowMatch = models.lastRowMatch(id)
 
        if status == 'NOT STARTED' and lastRowMatch is None:
            newmatch = models.MatchesEvents(id, last_changed, score, 0, status)
            matches_toupdate.append(newmatch)

        if lastRowMatch is not None:
            lastevent=lastRowMatch.event_id
            if status == 'FINISHED' and lastRowMatch.status != 'FINISHED':
                list_messages.append({'match': match, 'event': 'endgame'})
                newmatch = models.MatchesEvents(id, last_changed, score, 0, status,lastevent)
                matches_toupdate.append(newmatch)

        if status not in ['NOT STARTED', 'FINISHED']:
            if lastRowMatch is not None:
                elapsed = int(
                    (last_changed - lastRowMatch.last_update)
                    .total_seconds() / 60)
                if event != 'False':
                    event_url=event
                    result=EventAPICall(event_url)
                    events=result['event']
                    id_event=max(events, key=lambda x:x['sort'])
                    if id_event['sort'] != lastRowMatch.event_id:
                        if id_event['event'] == 'YELLOW CARD':
                            list_messages.append({'match': match, 'event': 'yellowcard'})
                            newmatch = models.MatchesEvents(
                                id, last_changed, score, 0, status,id_event['sort'])
                            matches_toupdate.append(newmatch)
                            

                # check if match has just started
                if lastRowMatch.status == 'NOT STARTED':
                    newmatch = models.MatchesEvents(
                        id, last_changed, score, 0, status,0)
                    matches_toupdate.append(newmatch)
                    scheduler.add_job(messageDuringMatch30, 'date', run_date=datetime.now()+datetime.timedelta(hours=0, minutes=30),args=[match,cumulated_time])
                    list_messages.append({'match': match, 'event': 'startgame'})

                if (status == 'HALF TIME BREAK' and lastRowMatch.status != 'HALF TIME BREAK'):
                    newmatch = models.MatchesEvents(
                        id, last_changed, score, 0, status, lastevent=lastRowMatch.event_id)
                    matches_toupdate.append(newmatch)
                    list_messages.append(
                        {'match': match, 'event': 'halftime'})

                if (status != 'HALF TIME BREAK' and lastRowMatch.status == 'HALF TIME BREAK'):
                    newmatch = models.MatchesEvents(
                        id, last_changed, score, 0, status, lastevent=lastRowMatch.event_id)
                    matches_toupdate.append(newmatch)
                    list_messages.append(
                        {'match': match, 'event': 'endhalftime'})

                newgoal = score.replace(" ", "") != lastRowMatch.score.replace(" ", "")
                cumulated_time += elapsed
                if newgoal and (score.replace(" ", "") != "0-0"):
                    newmatch = models.MatchesEvents(
                        id, last_changed, score, 0, status, lastevent=lastRowMatch.event_id)
                    matches_toupdate.append(newmatch)
                    goal1_now = int(score.replace(" ", "").split('-')[0])
                    goal2_now = int(score.replace(" ", "").split('-')[1])
                    goal1_before = int(lastRowMatch.score.replace(" ", "").split('-')[0])
                    if goal1_now == goal2_now:
                        event_str = "equalizer"
                    else:
                        if goal1_now > goal1_before:
                            event_str = "goal1"
                        else:
                            event_str = "goal2"
                    list_messages.append({'match': match, 'event': event_str})

            else:
                newmatch = models.MatchesEvents(
                    id, last_changed, score, 0, status,0)
                matches_toupdate.append(newmatch)

    for match in matches_toupdate:
        match.cumulatedTime = cumulated_time
        db.session.add(match)
        db.session.commit()

    # add cumulated time of all matches taking place at the same time to the messages
    result = []
    for i in list_messages:
        i['cumulated_time'] = cumulated_time
        result.append(i)
    return result


def updateTasks():
    list_fixtures = FixtureAPICall()
    for job in scheduler.get_jobs():
         if job.id != 'update' and job.id != 'live':
            job.remove()
    translation = pickle.load( open( "./data/translation.p", "rb" ) )
    with open("./data/short_name.csv", "r") as filestream:
        hashtags = dict()
        for line in filestream:
            currentline = line.strip().split(",")
            hashtags[currentline[0]] = currentline[1]
    for fixture in list_fixtures:
        translation[fixture['away_name']]={'translation': fixture['away_translations'],'hashtag':hashtags[fixture['away_name']]}
        translation[fixture['home_name']]={'translation': fixture['home_translations'],'hashtag':hashtags[fixture['home_name']]}
        datelocal = datetime.strptime(
            fixture['date']+" "+fixture['time'], '%Y-%m-%d %H:%M:%S') 
        datebefore = datelocal - timedelta(hours=0, minutes=25)
        scheduler.add_job(messageBeforeMatch30, 'date', run_date=datebefore, args=[fixture],)
        datebefore = datelocal - timedelta(hours=0, minutes=10)
        scheduler.add_job(messageBeforeMatch10, 'date', run_date=datebefore, args=[fixture],)
    #pickle.dump( translation, open( "./data/translation.p", "wb" ) )
    #print(translation)

@app.route('/')
def index():
    return render_template("index.html", sse_url=website_sse_url)

@app.route('/jobs')
def checkJobs():
    jobs = scheduler.get_jobs()
    my_list = []
    for job in jobs:
        if job.id != 'update' and job.id != 'live':
            date_job = job.next_run_time
            fixture = job.args[0]
            translations=pickle.load( open( "./data/translation.p", "rb" ) )
            hashtag="#"+translations[fixture['home_name']]['hashtag']+translations[fixture['away_name']]['hashtag']
            my_list.append([date_job, hashtag,translations[fixture['home_name']]['translation']['fr'], translations[fixture['away_name']]['translation']['fr'], fixture['date']+" "+fixture['time']])
    return render_template("jobs.html", my_list=my_list)


@app.route('/checkLiveScoreAPI')
def check_LiveScoreAPI():
    with app.app_context():       
        result = extractData(LiveAPICall())
# TODO REMOVE limit
        for msg in result:
            print("messenger --> new message")
            sse.publish(msg, type=msg['event'])
        return 'OK'


scheduler.add_job(updateTasks, 'cron', hour=3, minute=30, id='update')
# TODO change to minute
scheduler.add_job(check_LiveScoreAPI, 'interval', minutes=2, id='live', next_run_time=datetime.now())
updateTasks()
print('---------- start scheduler')
scheduler.start()
print(scheduler.get_jobs())

if __name__ == '__main__':
    app.run(debug=True)
