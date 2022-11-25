import requests
from .tools import get_env_variable
from requests.packages.urllib3.exceptions import InsecureRequestWarning

api_key = get_env_variable("livescore_api_key")
live_api_url = get_env_variable("livescore_api_url")
fixture_api_url = get_env_variable("fixture_api_url")
api_secret = get_env_variable("livescore_api_secret")
live_url = "{}scores/live.json?competition_id=362&key={}&secret={}".format(
    live_api_url, api_key, api_secret)
fixture_url = '{}matches.json?competition_id=362&date=today&key={}&secret={}'.format(
    fixture_api_url, api_key, api_secret)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def EventAPICall(event_url):
    live_events = requests.get(event_url,verify=False)
    events = live_events.json()
    return events

def FixtureAPICall():
    while True:
        list_fixtures = []
        fixtures = requests.get(fixture_url,verify=False).json()
        for fixture in fixtures['data']['fixtures']:
            print(fixture)
            list_fixtures.append(fixture)
  #      if fixtures['data']['next_page'] == 'false':
        break
    return list_fixtures


def LiveAPICall():
    live_events = requests.get(live_url,verify=False)
    events = live_events.json()
    return events


def main():
    LiveAPICall()


if __name__ == "__main__":
    main()
