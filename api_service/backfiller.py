#pub/sub code modified from quickstart samples
from flask import Flask
from flask import jsonify
import requests
import json
import time
from datetime import datetime, timedelta
from google.cloud import pubsub_v1
import config
import sys 


#base url for service: https://apicall-dot-sports-234417.appspot.com

def backfill_update(offset,match_counter):
    project_id = "sports-234417"
    topic_name = "today-games" #TODO: create new topic for yesterdays games
    yesterday_date = (datetime.today() - timedelta(offset)).date()
    matches = get_matches(yesterday_date)

    if matches: 
        for match in matches: 
            #pub(project_id,topic_name,match)
            pub(project_id,"yesterday-games",match)
            match_counter += 1
    else:
        print("No matches found for specified date: {0}".format(yesterday_date))
    return match_counter


#param date: python datetime object
def get_matches(date):
    matches = []
    endpoint = "https://apifootball.com/api/"
    key = config.key
    #from_date = "2019-04-21"
    #to_date = "2019-04-21"
    from_date = datetime.strftime(date,'%Y-%m-%d')
    to_date = from_date

    params = {"APIkey" : key, "action" : "get_events", "to": to_date, "from": from_date}
    response = requests.get(endpoint, params = params)

    leagues = ["62","117","109"] #premier league, bundesliga, la liga
    for match in response.json():
        try:
            
            if match["league_id"] in leagues:
                data = match
                matches.append(match)
        except: 
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

def backfill():
    match_counter = 0
    backfill_update(5,match_counter)
    return
    for i in range(121,213):
        match_counter = backfill_update(i,match_counter)
        time.sleep(5)
        if match_counter > 950: 
            sys.exit(i)

if __name__ == '__main__':
    backfill()