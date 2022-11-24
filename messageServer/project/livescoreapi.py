import requests
import datetime
from . import models
from .messenger import db
from .messenger import get_env_variable

api_key = get_env_variable("livescore_api_key")
live_api_url = get_env_variable("livescore_api_url")
fixture_api_url = get_env_variable("fixture_api_url")
api_secret = get_env_variable("livescore_api_secret")
live_url = "{}scores/live.json?competition_id=362&key={}&secret={}".format(
    live_api_url, api_key, api_secret)
# TODO remove today and replace by world CUP key
fixture_url = '{}matches.json?competition_id=362&date=today&key={}&secret={}'.format(
    fixture_api_url, api_key, api_secret)

# TODO add logs in files


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

        last_changed = datetime.datetime.strptime(
            match['last_changed'], '%Y-%m-%d %H:%M:%S')

        status = match['status']
        score = match['score']
        lastRowMatch = models.lastRowMatch(id)

        if status == 'NOT STARTED' and lastRowMatch is None:
            newmatch = models.MatchesEvents(id, last_changed, score, 0, status)
            matches_toupdate.append(newmatch)

        if lastRowMatch is not None:
            if status == 'FINISHED' and lastRowMatch.status != 'FINISHED':
                list_messages.append({'match': match, 'event': 'endgame'})
                newmatch = models.MatchesEvents(id, last_changed, score, 0, status)
                matches_toupdate.append(newmatch)

        if status not in ['NOT STARTED', 'FINISHED']:
            if lastRowMatch is not None:
                elapsed = int(
                    (last_changed - lastRowMatch.last_update)
                    .total_seconds() / 60)

                # check if match has just started
                if lastRowMatch.status == 'NOT STARTED':
                    newmatch = models.MatchesEvents(
                        id, last_changed, score, 0, status)
                    matches_toupdate.append(newmatch)
                    list_messages.append({'match': match, 'event': 'startgame'})

                if (status == 'HALF TIME BREAK' and lastRowMatch.status != 'HALF TIME BREAK'):
                    newmatch = models.MatchesEvents(
                        id, last_changed, score, 0, status)
                    matches_toupdate.append(newmatch)
                    list_messages.append(
                        {'match': match, 'event': 'halftime'})

                if (status != 'HALF TIME BREAK' and lastRowMatch.status == 'HALF TIME BREAK'):
                    newmatch = models.MatchesEvents(
                        id, last_changed, score, 0, status)
                    matches_toupdate.append(newmatch)
                    list_messages.append(
                        {'match': match, 'event': 'endhalftime'})

                newgoal = score.replace(" ", "") != lastRowMatch.score.replace(" ", "")
                cumulated_time += elapsed
                if newgoal and (score.replace(" ", "") != "0-0"):
                    newmatch = models.MatchesEvents(
                        id, last_changed, score, 0, status)
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
                    id, last_changed, score, 0, status)
                matches_toupdate.append(newmatch)

    for match in matches_toupdate:
        match.cumulatedTime = cumulated_time
        db.session.add(match)
        db.session.commit()

    # add cumulated time of all matches to the messages
    result = []
    for i in list_messages:
        i['cumulated_time'] = cumulated_time
        result.append(i)
    return result


def FixtureAPICall():
    while True:
        list_fixtures = []
        fixtures = requests.get(fixture_url,verify=False).json()
        for fixture in fixtures['data']['fixtures']:
            list_fixtures.append(fixture)
#        if fixtures['data']['next_page'] == 'false':
# TODO: remove that for  WC
        break
    return list_fixtures


def LiveAPICall():
    live_events = requests.get(live_url,verify=False)
    events = live_events.json()
    return extractData(events)


def main():
    LiveAPICall()


if __name__ == "__main__":
    main()
