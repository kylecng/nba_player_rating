from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

from flask import Flask
from flask import request
from flask import jsonify
app = Flask(__name__)
import time
import sys

@app.route('/')
def hello_world():
    return 'Hello to the World of F!'

@app.route('/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/d')
def get_d():
    req = request.get_json()
    req["hmmmmm"] = "hmmmmm"
    return req

headers = {}
stats = {}
metadata = {}
mean = {}
std = {}
hmin = {}
hmax = {}
def get_daily_data():
    global headers
    global stats
    global metadata
    global mean
    global std
    global hmin
    global hmax
    # NBA season we will be analyzing
    year = 2020
    # URL page we will scraping (see image above)
    url = "https://www.basketball-reference.com/leagues/NBA_{}_per_game.html".format(year)
    # this is the HTML from the given URL
    html = urlopen(url)
    soup = BeautifulSoup(html,features="html.parser")


    # use findALL() to get the column headers
    soup.findAll('tr', limit=2)
    # use getText()to extract the text we need into a list
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
    # exclude the first column as we will not need the ranking order from Basketball Reference for the analysis
    headers = headers[1:]


    # avoid the first header row
    rows = soup.findAll('tr')[1:]
    player_stats = [[td.getText() for td in rows[i].findAll('td')]
                for i in range(len(rows))]


    stats = pd.DataFrame(player_stats, columns = headers)
    stats.head(10)

    metadata = {'eFG%': {'numeric': 1, 'negative': 0}, '2PA': {'numeric': 1, 'negative': 0}, 'Pos': {'numeric': 0, 'negative': 0}, 'Age': {'numeric': 1, 'negative': 0}, 'FG%': {'numeric': 1, 'negative': 0}, '3P': {'numeric': 1, 'negative': 0}, 'PF': {'numeric': 1, 'negative': 1}, 'PTS': {'numeric': 1, 'negative': 0}, 'STL': {'numeric': 1, 'negative': 0}, 'FGA': {'numeric': 1, 'negative': 0}, '2P%': {'numeric': 1, 'negative': 0}, 'FTA': {'numeric': 1, 'negative': 0}, '3PA': {'numeric': 1, 'negative': 0}, 'DRB': {'numeric': 1, 'negative': 0}, 'FT%': {'numeric': 1, 'negative': 0}, 'FG': {'numeric': 1, 'negative': 0}, 'Tm': {'numeric': 0, 'negative': 0}, 'MP': {'numeric': 1, 'negative': 0}, 'Player': {'numeric': 0, 'negative': 0}, 'G': {'numeric': 1, 'negative': 0}, 'TRB': {'numeric': 1, 'negative': 0}, 'BLK': {'numeric': 1, 'negative': 0}, 'TOV':
{'numeric': 1, 'negative': 1}, 'ORB': {'numeric': 1, 'negative': 0}, 'AST': {'numeric': 1, 'negative': 0}, 'FT': {'numeric': 1, 'negative': 0}, 'GS': {'numeric': 1, 'negative': 0}, '2P': {'numeric': 1, 'negative': 0}, '3P%': {'numeric': 1, 'negative': 0}}
    for header in headers:
        stats[header] = pd.to_numeric(stats[header],errors='ignore')
    # stats = stats.drop(['Age','G','GS','MP'],axis=1)
    # stats = stats.drop(['Age','G','GS','MP','FGA','3PA','2P','2PA','eFG%','FTA','ORB','DRB','PF','FT','2P%','3P%','FG'],axis=1)

    headers = list(stats)
    mean = stats.mean(axis=0)
    std = stats.std(axis=0)
    # for header in metadata:
    #     if metadata[header]["numeric"] == 1:
    #         if metadata[header]["negative"] == 1:
    #             hmax[header] = stats[header].min()
    #         else:
    #             hmax[header] = stats[header].max()
    # for header in metadata:
    #     if metadata[header]["numeric"] == 1:
    #         if metadata[header]["negative"] == 1:
    #             hmin[header] = stats[header].max()
    #         else:
    #             hmin[header] = stats[header].min()
    hmin = stats.min()
    hmax = stats.max()
    # print(mean)
    # print(std)

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
    # print(req)
    hs = headers
    ss = stats

    weights = {'3P':1,'FT':1,'TRB':1,'AST':1,'STL':1,'BLK':1,'TOV':1,'PTS':1,'Age':0,'G':0,'GS':0,'MP':0,'FG':0,'FGA':0,'FG%':0,'3PA':0,'3P%':0,'2P':0,'2PA':0,'2P%':0,'eFG%':0,'FTA':0,'FT%':0,'ORB':0,'DRB':0,'PF':0}

    to_remove = []
    for header in hs:
        if header in weights.keys() and weights[header] == 0:
            to_remove.append(header)
    ss = ss.drop(to_remove,axis=1)


    for header in req.keys():
        try:
            weights[header] = float(req[header])
        except ValueError:
            weights[header] = 0

        
    hs = list(ss)
    scores = []
    for header in hs:
        if metadata[header]["numeric"] == 1 and header in weights.keys() and weights[header] != 0 and header in hs:
            scores.append("$$"+header)
            if metadata[header]["negative"] == 1:
                ss["$$"+header] = weights[header] * (mean[header]-ss[header]) / std[header]
            else:
                ss["$$"+header] = weights[header] * (ss[header]-mean[header]) / std[header]

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
            percentile.append("++"+header)
            
            if metadata[header]["negative"] == 1:
                ss["++"+header] = ((ss[header]-mean[header]) / (hmin[header] - mean[header]))
            else:
                ss["++"+header] = ((ss[header]-mean[header]) / (hmax[header] - mean[header]))


    hs = list(ss)


    # to_remove = hs.copy()
    # for header in hs:
    #     if not header.startswith("$$"):
    #         to_remove.remove(header)
    # ss = ss.drop(to_remove,axis=1)



    ss = ss.round(3)
    # print(ss)
    # return ss.to_json(orient='index')
    return jsonify({"data": ss.to_json(orient='index'), "metadata":metadata, "minImpact": minImpact, "maxImpact": maxImpact})

get_daily_data()
if __name__ == '__main__':
    app.run()




