import pymongo
import numpy as np
import importlib
import tensorflow as tf
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from keras.models import load_model
from sklearn.externals import joblib
from sklearn.preprocessing import StandardScaler,LabelBinarizer
from keras import backend as K
import os
import config


app = Flask(__name__)

#init model, normalizer, tensorflow session
model = load_model('soccer_odds_model.h5')
normalizer = joblib.load('normalizer.pkl') 
graph = tf.get_default_graph()
init_op = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init_op)

#prediction POST endpoint 
@app.route('/predict',methods=['POST'])
def predict():
    data = request.get_json(force=True)
    home_team = data["home_team"]
    away_team = data["away_team"]
    date = data["match_date"]

    #connect to mongoDB
    client = pymongo.MongoClient(config.connection_string)
    collection = client.matchdb.matchmaster

    #Get 10 latest matches for each team excluding current match
    home_matches, curr_match = get_matches(home_team,date,collection)
    away_matches, _ = get_matches(away_team,date,collection)
    #aggregate features and format correctly for model
    home_arr = agg_values(home_matches,home_team)
    away_arr = agg_values(away_matches,away_team)
    odds_arr = np.array([curr_match["home_odds"],curr_match["draw_odds"],curr_match["away_odds"]])
    temp_arr = np.append(home_arr,away_arr)
    pred_input = np.array([(list(np.append(odds_arr,temp_arr)))])

    #normalize input params and get predictions
    pred_input = normalizer.transform(pred_input)
    with graph.as_default():
        prediction = model.predict(pred_input)[0]
    pred_dict = {"model_away":float(prediction[0]),"model_draw":float(prediction[1]), "model_home":float(prediction[2])}
    return jsonify(pred_dict)

#gets 10 most recent matches for a team excluding the current date from Mongo
def get_matches(team, date,collection):
    pred_filter = {"$or":[ {"away_team":team}, {"home_team":team} ]}
    matches = list(collection.find(pred_filter))
    curr_match = [match for match in matches if match["match_date"] == date]
    matches = [match for match in matches if match["match_date"] != date][:]
    for match in matches:
        match["match_date"] = datetime.strptime(match["match_date"],'%Y-%m-%d')
    curr_date = datetime.strptime(date,'%Y-%m-%d')
    matches = [match for match in matches if match["match_date"] < curr_date][:]
    matches = sorted(matches, key = lambda x: x["match_date"])
    matches = matches[-10:]
    return matches,curr_match[0]

#Aggregates features for model prediction
def agg_values(matches,team):
    wins = 0
    losses = 0
    draws = 0
    goals = 0
    opp_goals = 0
    shots = 0
    shots_on = 0
    opp_shots = 0
    opp_shots_on = 0
    for match in matches:
        if match["home_team"] == team: 
            prefix = "home_"
            opp_prefix = "away_"
        if match["away_team"] == team: 
            prefix = "away_"
            opp_prefix = "home_"
        if match[prefix + "score"] > match[opp_prefix + "score"]:
            wins += 1
        elif match[prefix + "score"] < match[opp_prefix + "score"]:
            losses += 1
        elif match[prefix + "score"] == match[opp_prefix + "score"]:
            draws += 1
        else:
            print(match)
        goals += match[prefix + "score"]
        opp_goals += match[opp_prefix + "score"]
        shots += match[prefix + "shots_on_target"] + match[prefix + "shots_off_target"]
        shots_on += match[prefix + "shots_on_target"]
        opp_shots += match[opp_prefix + "shots_on_target"] + match[opp_prefix + "shots_off_target"]
        opp_shots_on += match[opp_prefix + "shots_on_target"]

    return np.array([wins,draws,losses,goals,opp_goals,shots,shots_on,opp_shots,opp_shots_on])


if __name__ == '__main__':
    app.run(port=5000, debug=False)