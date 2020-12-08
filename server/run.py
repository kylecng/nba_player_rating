from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

from flask import Flask
from flask import request
from flask import jsonify
app = Flask(__name__)
import time
import sys


ratingID = 'rating'
percentileID = 'blahblah'

@app.route('/')
def hello_world():
    return 'Hello to the World of F!'

headers = {}
stats = {}
metadata = {}
mean = {}
std = {}
hmin = {}
hmax = {}
def get_daily_data(year):
    global headers
    global stats
    global metadata
    global mean
    global std
    global hmin
    global hmax
   

    
    url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
    html = urlopen(url)
    soup = BeautifulSoup(html,features="html.parser")



    soup.findAll('tr', limit=2)
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
    headers = headers[1:]

    rows = soup.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')]
                for i in range(len(rows))]


    stats = pd.DataFrame(player_stats, columns = headers)
    stats.head(10)

#     metadata = {'eFG%': {'numeric': 1, 'negative': 0}, '2PA': {'numeric': 1, 'negative': 0}, 'Pos': {'numeric': 0, 'negative': 0}, 'Age': {'numeric': 1, 'negative': 0}, 'FG%': {'numeric': 1, 'negative': 0}, '3P': {'numeric': 1, 'negative': 0}, 'PF': {'numeric': 1, 'negative': 1}, 'PTS': {'numeric': 1, 'negative': 0}, 'STL': {'numeric': 1, 'negative': 0}, 'FGA': {'numeric': 1, 'negative': 0}, '2P%': {'numeric': 1, 'negative': 0}, 'FTA': {'numeric': 1, 'negative': 0}, '3PA': {'numeric': 1, 'negative': 0}, 'DRB': {'numeric': 1, 'negative': 0}, 'FT%': {'numeric': 1, 'negative': 0}, 'FG': {'numeric': 1, 'negative': 0}, 'Tm': {'numeric': 0, 'negative': 0}, 'MP': {'numeric': 1, 'negative': 0}, 'Player': {'numeric': 0, 'negative': 0}, 'G': {'numeric': 1, 'negative': 0}, 'TRB': {'numeric': 1, 'negative': 0}, 'BLK': {'numeric': 1, 'negative': 0}, 'TOV':
# {'numeric': 1, 'negative': 1}, 'ORB': {'numeric': 1, 'negative': 0}, 'AST': {'numeric': 1, 'negative': 0}, 'FT': {'numeric': 1, 'negative': 0}, 'GS': {'numeric': 1, 'negative': 0}, '2P': {'numeric': 1, 'negative': 0}, '3P%': {'numeric': 1, 'negative': 0}}
    
    for header in headers:
        stats[header] = pd.to_numeric(stats[header],errors='ignore')
    headers = list(stats)
    mean = stats.mean(axis=0)
    std = stats.std(axis=0)
    hmin = stats.min()
    hmax = stats.max()

@app.route('/data',methods=['GET', 'POST'])
def get_data():
    global headers
    global stats
    global metadata
    global mean
    global std
    global hmin
    global hmax
    req = request.get_json()
    weights = req['weights']
    metadata = req['metadata']
    includeds = req['includeds']
    print('WEIGHTS',weights)
    print('METADATA',metadata)
    hs = headers
    ss = stats

    # weights = {'3P':1,'FT':1,'TRB':1,'AST':1,'STL':1,'BLK':1,'TOV':1,'PTS':1,'Age':0,'G':0,'GS':0,'MP':0,'FG':0,'FGA':0,'FG%':0,'3PA':0,'3P%':0,'2P':0,'2PA':0,'2P%':0,'eFG%':0,'FTA':0,'FT%':0,'ORB':0,'DRB':0,'PF':0}
    
    to_remove = []
    for header in hs:
        if header in weights.keys() and not includeds[header]:
            to_remove.append(header)
        elif header not in metadata.keys():
            to_remove.append(header)
    ss = ss.drop(to_remove,axis=1)


    # for header in reqWeights.keys():
    #     try:
    #         weights[header] = float(reqWeights[header])
    #     except ValueError:
    #         weights[header] = 0

        
    hs = list(ss)
    scores = []
    for header in hs:
        if header in includeds.keys() and metadata[header]["numeric"] == 1 and header in weights.keys() and weights[header] != 0 and header in hs:
            scores.append(ratingID+header)
            if metadata[header]["negative"] == 1:
                ss[ratingID+header] = weights[header] * (mean[header]-ss[header]) / std[header]
            else:
                ss[ratingID+header] = weights[header] * (ss[header]-mean[header]) / std[header]

    minImpact = ss[scores].min().min()
    maxImpact = ss[scores].max().max()
    print(scores)
    print(minImpact)
    print(maxImpact)

    ss['SCORE'] = ss[scores].sum(axis=1)
    ss = ss.sort_values(by='SCORE',ascending=False)


    percentile = []
    for header in hs:
        if metadata[header]["numeric"] == 1 and header in weights.keys() and weights[header] != 0 and header in hs:
            percentile.append(percentileID+header)
            
            if metadata[header]["negative"] == 1:
                ss[percentileID+header] = ((ss[header]-mean[header]) / (hmin[header] - mean[header]))
            else:
                ss[percentileID+header] = ((ss[header]-mean[header]) / (hmax[header] - mean[header]))


    hs = list(ss)

    ss = ss.round(3)
    print(ss)
    
    return jsonify({"data": ss.to_json(orient='index'), "metadata":metadata, "minImpact": minImpact, "maxImpact": maxImpact})

get_daily_data(2020)
if __name__ == '__main__':
    app.run()




