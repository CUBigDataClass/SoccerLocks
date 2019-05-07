import json
import requests
import pymongo
import dns
import config

#process a match message for a game occuring today
def process_message(message):
    #decode message 
    try:
        data  = message.data.decode('utf-8')
        match = json.loads(data)
    except:
        print("Failed to parse data for message: {0}".format(message))
        return

    #set basic information in match dict 
    match_agg = {}
    match_agg["home_team"] = match["match_hometeam_name"]
    match_agg["away_team"] = match["match_awayteam_name"]
    match_agg["match_date"] = match["match_date"]
    match_agg["time"] = match["match_time"]
    match_agg["home_score"] = None
    match_agg["away_score"] = None
    match_agg["home_half_score"] = None
    match_agg["away_half_score"] = None
    match_agg = null_stats(match_agg)

    #get odds from odds API for this match
    endpoint = "https://apifootball.com/api/"
    key = config.key
    from_date = match["match_date"]
    to_date = match["match_date"]
    match_id = match["match_id"]    
    params = {"APIkey" : key, "action" : "get_odds", "to": to_date, "from": from_date,"match_id": match_id}
    odds_response = requests.get(endpoint, params = params) 

    #set odds in match dict if response is succesful
    if not "error" in odds_response.json():
        odds = odds_response.json()[0]
        match_agg["home_odds"] = tofloat(odds.get("odd_1"))
        match_agg["draw_odds"] = tofloat(odds.get("odd_x"))
        match_agg["away_odds"] = tofloat(odds.get("odd_2"))
    else: 
        match_agg["home_odds"] = None
        match_agg["draw_odds"] = None
        match_agg["away_odds"] = None

    match_agg["model_home"] = None
    match_agg["model_draw"] = None
    match_agg["model_away"] = None

    match_agg["full_match_stats"] = False 
    print(match_agg) #easy logging, this will appear in StackDriver

    #connect to mongo and insert match document
    client = pymongo.MongoClient(config.connection_string)
    collection = client.matchdb.matchmaster
    filter = {'match_date': match_agg["match_date"],'home_team':match_agg['home_team'],'away_team':match_agg['away_team']}
    data = collection.find_one(filter)
    #only insert when match is not already in db 
    if not data: 
        _id = collection.insert_one(match_agg)

    #get model predictions from prediction API 
    endpoint = "https://predictor-dot-sports-234417.appspot.com/predict"
    params = {'home_team':match_agg["home_team"],'away_team':match_agg["away_team"],'match_date':match_agg["match_date"]}
    predictor_response = requests.post(endpoint, json = params)
    #update document in mongo if response is successful
    if predictor_response.status_code == 200:
        print(predictor_response.json())
        predictions = predictor_response.json()
        match_agg["model_home"] = predictions["model_home"]
        match_agg["model_draw"] = predictions["model_draw"]
        match_agg["model_away"] = predictions["model_away"]
        filter = {'match_date': match_agg["match_date"],'home_team':match_agg['home_team'],'away_team':match_agg['away_team']}
        update_data = {'$set': match_agg}
        data = collection.find_one_and_update(filter,update_data,upsert=True)
        print(data)

    return 0 

#Custom int conversion to handle empty stats from API
def toint(num):
    try:
        intnum = int(num)
    except (ValueError, TypeError):
        intnum = None
    return intnum

#Custom float conversion to handle empty stats from API
def tofloat(num):
    try:
        floatnum = float(num)
    except (ValueError, TypeError):
        floatnum = None
    return floatnum

#init all stats as null (not available until game is over)
def null_stats(match_agg):
    match_agg["home_shots_on_target"] = None
    match_agg["away_shots_on_target"] = None
    match_agg["home_shots_off_target"] = None
    match_agg["away_shots_off_target"] = None
    match_agg["home_corners"] = None
    match_agg["away_corners"] = None
    match_agg["home_offsides"] = None
    match_agg["away_offsides"] = None
    match_agg["home_fouls"] = None
    match_agg["away_fouls"] = None
    match_agg["home_yellow_cards"] = None
    match_agg["away_yellow_cards"] = None
    match_agg["home_goal_kicks"] = None
    match_agg["away_goal_kicks"] = None
    return match_agg