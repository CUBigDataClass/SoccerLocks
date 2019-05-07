import json
import requests
import pymongo
import dns
import config

#process a match message for a match occuring yesterday
def process_message(message):
    try:
        data  = message.data.decode('utf-8')
        match = json.loads(data)
    except Exception as e:
        print("Failed to parse data for message: {0}".format(message))
        return

    #parse out all match stats from message and assign to match dict
    match_agg = {}
    match_agg["home_team"] = match["match_hometeam_name"]
    match_agg["away_team"] = match["match_awayteam_name"]
    match_agg["match_date"] = match["match_date"]
    match_agg["time"] = match["match_time"]
    match_agg["home_score"] = toint(match.get("match_hometeam_score"))
    match_agg["away_score"] = toint(match.get("match_awayteam_score"))
    match_agg["home_half_score"] = toint(match.get("match_hometeam_halftime_score"))
    match_agg["away_half_score"] = toint(match.get("match_awayteam_halftime_score"))
    for stat in match["statistics"]:
        if stat["type"] == "shots on target":
            match_agg["home_shots_on_target"] = toint(stat.get("home"))
            match_agg["away_shots_on_target"] = toint(stat.get("away"))
        elif stat["type"] == "shots off target":
            match_agg["home_shots_off_target"] = toint(stat.get("home"))
            match_agg["away_shots_off_target"] = toint(stat.get("away"))
        elif stat["type"] == "corners":
            match_agg["home_corners"] = toint(stat.get("home"))
            match_agg["away_corners"] = toint(stat.get("away"))
        elif stat["type"] == "offsides":
            match_agg["home_offsides"] = toint(stat.get("home"))
            match_agg["away_offsides"] = toint(stat.get("away"))
        elif stat["type"] == "fouls":
            match_agg["home_fouls"] = toint(stat.get("home"))
            match_agg["away_fouls"] = toint(stat.get("away"))
        elif stat["type"] == "yellow cards":
            match_agg["home_yellow_cards"] = toint(stat.get("home"))
            match_agg["away_yellow_cards"] = toint(stat.get("away"))
        elif stat["type"] == "goal kicks":
            match_agg["home_goal_kicks"] = toint(stat.get("home"))
            match_agg["away_goal_kicks"] = toint(stat.get("away"))
    match_agg["full_match_stats"] = True
    #if stats missing from api response set to null
    if not match["statistics"]:
        match_agg["full_match_stats"] = False
        match_agg = null_stats(match_agg)

    #get odds from footballdata api
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
        match_agg["full_match_stats"] =False
        match_agg["home_odds"] = None
        match_agg["draw_odds"] = None
        match_agg["away_odds"] = None

    print(match_agg) #easy logging, this will appear in StackDriver

    #update existing match document in mongo
    client = pymongo.MongoClient(config.connection_string)
    collection = client.matchdb.matchmaster
    filter = {'match_date': match_agg["match_date"],'home_team':match_agg['home_team'],'away_team':match_agg['away_team']}
    update_data = {'$set': match_agg}
    collection.find_one_and_update(filter,update_data,upsert=True)

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
        floatnum = Nones
    return floatnum

#init all stats as null (used when stats are missing from api)
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
