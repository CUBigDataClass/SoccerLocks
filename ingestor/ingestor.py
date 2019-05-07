#pub/sub code modified from quickstart samples
from flask import Flask
from flask import jsonify
import requests
import json
import time
from datetime import datetime, timedelta
from google.cloud import pubsub_v1
import config

app = Flask(__name__)

#base url for service: https://apicall-dot-sports-234417.appspot.com

#test 
@app.route('/')
def hello():
    dictionary = {'message': 'Different message for service'}
    return jsonify(dictionary)

#todays games update endpoint run daily through cron job
@app.route('/ingestor/today-games/update/',methods = ['GET'])
def today_update():
    project_id = "sports-234417"
    topic_name = "today-games"

    #get all matches for today and publish to today-games topic
    current_date = datetime.today().date() 
    matches = get_matches(current_date)
    if matches: 
        for match in matches: 
            print(match)
            pub(project_id,topic_name,match)
    else:
        print("No matches found for specified date: {0}".format(current_date))

    return jsonify(matches)

#yesterdays games update endpoint run daily though cron job
@app.route('/ingestor/yesterday-games/update/',methods = ['GET'])
def yesterday_update():
    project_id = "sports-234417"
    topic_name = "yesterday-games" 

    #get all matches for yesterday and publish to yesterday-games topic
    yesterday_date = (datetime.today() - timedelta(1)).date()
    matches = get_matches(yesterday_date)
    if matches: 
        for match in matches: 
            pub(project_id,topic_name,match)
    else:
        print("No matches found for specified date: {0}".format(yesterday_date))

    return jsonify(matches)


#get all matches for a specified date in supported leagues
def get_matches(date):
    matches = []
    endpoint = "https://apifootball.com/api/"
    key = config.key
    from_date = datetime.strftime(date,'%Y-%m-%d')
    to_date = from_date
    params = {"APIkey" : key, "action" : "get_events", "to": to_date, "from": from_date}
    response = requests.get(endpoint, params = params)

    #add all matches in supported leagues to list if api response successful
    leagues = ["62","117","109"] #premier league, bundesliga, la liga
    if "error" not in response.json():
        for match in response.json():
            if match["league_id"] in leagues:
                data = match
                matches.append(match)
    else:
        print(response.json())

    return matches


def get_callback(api_future, data):
    """Wrap message data in the context of the callback function."""

    def callback(api_future):
        try:
            print('\n')
           # print("Published message {} now has message ID {}".format(
           #     data, api_future.result()))
        except Exception:
            print("A problem occurred when publishing {}: {}\n".format(
                data, api_future.exception()))
            raise
    return callback


def pub(project_id, topic_name,match):
    """Publishes a message to a Pub/Sub topic."""

    client = pubsub_v1.PublisherClient()
    data = bytes(json.dumps(match),'utf-8')
    # Data sent to Cloud Pub/Sub must be a bytestring

    # When you publish a message, the client returns a future.
    topic_path = client.topic_path(project_id, topic_name)
    print("Publishing message with data: {0}".format(data))
    api_future = client.publish(topic_path, data=data)
    api_future.add_done_callback(get_callback(api_future, data))

    # Keep the main thread from exiting until background message
    # is processed.
    while api_future.running():
        time.sleep(0.1)
        

if __name__ == '__main__':
    app.run(debug=True)