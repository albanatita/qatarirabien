from flask import Flask, render_template
from flask_sse import sse
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta, datetime
import pickle


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)


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

db = SQLAlchemy(app)

db.init_app(app)

from . import livescoreapi    # here to avoid circular dependencies (yes poor structure of code)


scheduler = BackgroundScheduler()


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


def updateTasks():
    list_fixtures = livescoreapi.FixtureAPICall()
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
    pickle.dump( translation, open( "./data/translation.p", "wb" ) )
    # print(translation)

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
        app.logger.debug('Request from client for update on livescore api')
        result = livescoreapi.LiveAPICall()
# TODO REMOVE limit
        for msg in result:
            print("messenger --> new message")
            sse.publish(msg, type=msg['event'])
        return 'OK'


scheduler.add_job(updateTasks, 'cron', hour=3, minute=30, id='update')
# TODO change to minute
scheduler.add_job(check_LiveScoreAPI, 'interval', minutes=1, id='live', next_run_time=datetime.now())
updateTasks()
scheduler.start()
print(scheduler.get_jobs())

if __name__ == '__main__':
    app.run(debug=True)
