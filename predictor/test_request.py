import requests

# URL
url = 'http://localhost:5000/predict'
url = 'https://predictor-dot-sports-234417.appspot.com/predict'
json = {'home_team':"Sevilla",'away_team':"Girona",'match_date':"2019-04-28"}

r = requests.post(url,json=json)
print(r.json())
