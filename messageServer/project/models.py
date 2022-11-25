from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Game(db.Model):
    __tablename__ = 'public.game_list'
    id = db.Column('id', db.Integer, primary_key=True)
    name_team_1 = db.Column(db.String(100))
    name_team_2 = db.Column(db.String(100))
    location = db.Column(db.String(100))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    score = db.Column(db.String(20))

    def __init__(self, name_team_1, name_team_2, location, start_date):
        self.name_team_1 = name_team_1
        self.name_team_2 = name_team_2
        self.location = location
        self.start_date = start_date


class FloatingTweet(db.Model):
    __tablename__ = 'float_tweets_list'
    id = db.Column('id', db.Integer, primary_key=True)
    tweet_content = db.Column(db.String(200))
    language = db.Column(db.String(20))
    publish_date = db.Column(db.DateTime)
    repeat = db.Column(db.Integer)
    

    def __init__(self, tweet_content, language, publish_date, repeat):
        self.tweet_content = tweet_content
        self.language = language
        self.publish_date = publish_date
        self.repeat = repeat


class MatchesEvents(db.Model):
    __tablename__ = 'matches_events'
    id = db.Column('db_id', db.Integer, primary_key=True)
    id_match = db.Column('id_match', db.Integer)
    last_update = db.Column(db.DateTime)
    score = db.Column('score', db.String(20))
    cumulatedTime = db.Column('cumulated_time', db.Integer)
    status = db.Column(db.String(100))
    event_id = db.Column('event_id', db.Integer)

    def __init__(self, id_match, last_update, score, cumulatedTime, status,event):
        self.id_match = id_match
        self.last_update = last_update
        self.score = score
        self.cumulatedTime = cumulatedTime
        self.status = status
        self.event_id = event
        

# get last row a match with a given ID - None if match not yet in database


def lastRowMatch(id):
    result = MatchesEvents.query.filter_by(
        id_match=id).order_by(MatchesEvents.id.desc()).first()
    return result

# get last entry in the database (useful to get accumulated time)


def lastRow():
    result = MatchesEvents.query.order_by(MatchesEvents.id.desc()).first()
    return result
