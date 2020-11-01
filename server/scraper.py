from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd

weights = {}
year = 2019
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

metadata = {'eFG%': {'isNumeric': 1, 'negative': 0}, '2PA': {'isNumeric': 1, 'negative': 0}, 'Pos': {'isNumeric': 0, 'negative': 0}, 'Age': {'isNumeric': 1, 'negative': 0}, 'FG%': {'isNumeric': 1, 'negative': 0}, '3P': {'isNumeric': 1, 'negative': 0}, 'PF': {'isNumeric': 1, 'negative': 1}, 'PTS': {'isNumeric': 1, 'negative': 0}, 'STL': {'isNumeric': 1, 'negative': 0}, 'FGA': {'isNumeric': 1, 'negative': 0}, '2P%': {'isNumeric': 1, 'negative': 0}, 'FTA': {'isNumeric': 1, 'negative': 0}, '3PA': {'isNumeric': 1, 'negative': 0}, 'DRB': {'isNumeric': 1, 'negative': 0}, 'FT%': {'isNumeric': 1, 'negative': 0}, 'FG': {'isNumeric': 1, 'negative': 0}, 'Tm': {'isNumeric': 0, 'negative': 0}, 'MP': {'isNumeric': 1, 'negative': 0}, 'Player': {'isNumeric': 0, 'negative': 0}, 'G': {'isNumeric': 1, 'negative': 0}, 'TRB': {'isNumeric': 1, 'negative': 0}, 'BLK': {'isNumeric': 1, 'negative': 0}, 'TOV':
{'isNumeric': 1, 'negative': 1}, 'ORB': {'isNumeric': 1, 'negative': 0}, 'AST': {'isNumeric': 1, 'negative': 0}, 'FT': {'isNumeric': 1, 'negative': 0}, 'GS': {'isNumeric': 1, 'negative': 0}, '2P': {'isNumeric': 1, 'negative': 0}, '3P%': {'isNumeric': 1, 'negative': 0}}
for header in headers:
    stats[header] = pd.to_numeric(stats[header],errors='ignore')



