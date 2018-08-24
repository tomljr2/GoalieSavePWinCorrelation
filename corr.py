import requests
import json
from scipy.stats.stats import pearsonr

# Separate the url into parts that will change and then
# we will put them all together later so that we can automatically
# change the url in a loop
baseurl = "https://statsapi.web.nhl.com/api/v1/game/"
year = 2013
finalYear = 2017	# This is the first year of the last season, so 2017-2018, would just be 2017
gameType = 2
game = 1
goalies = []
decision = 0
fileName = "correlationStats.txt"
f = open(fileName,"w")

url = baseurl + str(year) + '{0:02d}'.format(gameType) + '{0:04d}'.format(game) + '/boxscore'
response = requests.get(url).json()

while year <= finalYear:
   while (year < 2017 and game <= 1230) or (year <= 2017 and game <= 1271):
      # Go through both home and away teams
      try:
         for teams in response["teams"]:
            # Go through all players
            for players in response["teams"][teams]["players"]:
               # Make sure the player is a goalie and they were credited with the win or the loss
               if response["teams"][teams]["players"][players]["position"]["abbreviation"] == "G" \
                  and response["teams"][teams]["players"][players]["stats"]["goalieStats"]["decision"]:
                     try:
                        # Make a decision a 0 or 1 instead of L or W
                        if response["teams"][teams]["players"][players]["stats"]["goalieStats"]["decision"] == "W":
                           decision = 1
                        else:
                           decision = 0
                        # Check if the player is in the list already, if not, add him
                        if not any(e[0] == players[2:] for e in goalies): #not in [i for i, v in enumerate(goalies) if v[0] == players[2:]]:
                           # Add the ID, name, save percentage, and decision
                           goalies.append([players[2:], \
                                           response["teams"][teams]["players"][players]["person"]["fullName"], \
                                           [response["teams"][teams]["players"][players]["stats"]["goalieStats"]["savePercentage"]],
                                           [decision]])
                        # If they already exist in the list, then we need to update their
                        # save percentages and wins/losses
                        else:
                           # This is a bit hard to read, but all I am doing is searching for the player's ID and
                           # getting the first instance of the index (there should only be one). Then, I will append
                           # their save percentage and decision to the lists in the tuple
                           goalies[[v[0] for v in goalies].index(players[2:])][2].append( \
                              response["teams"][teams]["players"][players]["stats"]["goalieStats"]["savePercentage"])
                           goalies[[v[0] for v in goalies].index(players[2:])][3].append(decision)
                     except KeyError:
                        pass
      except KeyError:
         pass
      game = game + 1
      url = baseurl + str(year) + '{0:02d}'.format(gameType) + '{0:04d}'.format(game) + '/boxscore'
      response = requests.get(url).json()
   game = 1
   year = year + 1
   url = baseurl + str(year) + '{0:02d}'.format(gameType) + '{0:04d}'.format(game) + '/boxscore'
   response = requests.get(url).json()

string = "Correlations\n\n"

for goalie in goalies:
   string = string + goalie[1]
   string = string + "\n" + str(len(goalie[2]))
   string = string + "\n" + str(pearsonr(goalie[2],goalie[3])[0]) + "\n\n"

f.write(string)
