import mysql.connector
import json
from nba_api.stats.static import players
import subprocess

def connect_to_db():
    return mysql.connector.connect(
        host="rpdef-db",
        user="root",
        password="password",
        port=3306,
        database="rpdef",
    )

def insert(traditional, lt10, gt10, player_positions, season):
    mydb = connect_to_db()
    mycursor = mydb.cursor()

    for index, row in traditional.iterrows():
        player = row['Player']
        if player in player_positions:
            sql = "INSERT INTO player (Player, Team, Age, GP, MIN, PTS, FGM, FGA, FG, 3PM, 3PA, 3P, FTM, FTA, FT, OREB, DREB, REB, AST, TOV, STL, BLK, PF, PlusMinus, Position, Stop1Perimeter, Stop2Perimeter, StopPerimeter, AverageTeamStopPerimeter, PlayerContributionPerimeter, TeamDefensePerimeter, PlayerTeamPerimeter, PDEF, Stop1Rim, Stop2Rim, StopRim, AverageTeamStopRim, PlayerContributionRim, TeamDefenseRim, PlayerTeamRim, RDEF, RPDEF, SeasonYear, NbaPlayerId) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = row.values.tolist()
            val.append(player_positions[player])
            if player in lt10:
                # Add stop1, stop2, stop
                val.extend([gt10[player][2], gt10[player][3], gt10[player][0]])
                # Add average_team_stops, player_contribution, team_defense, player_team, final_rating
                val.extend(gt10[player][4:])
                # Add stop1, stop2, stop
                val.extend([lt10[player][2], lt10[player][3], lt10[player][0]])
                # Add average_team_stops, player_contribution, team_defense, player_team, final_rating
                val.extend(lt10[player][4:])
                val.append(gt10[player][-1]+lt10[player][-1])
            else:
                val.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            val.append(season[-5:].replace("-", "/"))
            player_api = [player_api for player_api in players.get_players() if player_api['full_name'] == player]
            if player_api:
                val.append(player_api[0]['id'])
                mycursor.execute(sql, val)
                mydb.commit()

def update(traditional, lt10, gt10, player_positions, season):
    mydb = connect_to_db()
    mycursor = mydb.cursor()

    for index, row in traditional.iterrows():
        player = row['Player']
        if player in player_positions:
            sql = "UPDATE player SET Player = %s, Team = %s, Age = %s, GP = %s, MIN = %s, PTS = %s, FGM = %s, FGA = %s, FG = %s, 3PM = %s, 3PA = %s, 3P = %s, " \
                  "FTM = %s, FTA = %s, FT = %s, OREB = %s, DREB = %s, REB = %s, AST = %s, TOV = %s, STL = %s, BLK = %s, PF = %s, PlusMinus = %s, Position = %s, " \
                  "Stop1Perimeter = %s, Stop2Perimeter = %s, StopPerimeter = %s, AverageTeamStopPerimeter = %s, PlayerContributionPerimeter = %s, " \
                  "TeamDefensePerimeter = %s, PlayerTeamPerimeter = %s, PDEF = %s, Stop1Rim = %s, Stop2Rim = %s, StopRim = %s, AverageTeamStopRim = %s, " \
                  "PlayerContributionRim = %s, TeamDefenseRim = %s, PlayerTeamRim = %s, RDEF = %s, RPDEF = %s " \
                  "WHERE SeasonYear = %s AND NbaPlayerId = %s"
            val = row.values.tolist()
            val.append(player_positions[player])
            if player in lt10:
                # Add stop1, stop2, stop
                val.extend([gt10[player][2], gt10[player][3], gt10[player][0]])
                # Add average_team_stops, player_contribution, team_defense, player_team, final_rating
                val.extend(gt10[player][4:])
                # Add stop1, stop2, stop
                val.extend([lt10[player][2], lt10[player][3], lt10[player][0]])
                # Add average_team_stops, player_contribution, team_defense, player_team, final_rating
                val.extend(lt10[player][4:])
                val.append(gt10[player][-1] + lt10[player][-1])
            else:
                val.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            val.append(season[-5:].replace("-", "/"))
            player_api = [player_api for player_api in players.get_players() if player_api['full_name'] == player]
            if player_api:
                val.append(player_api[0]['id'])
                mycursor.execute(sql, val)
                mydb.commit()
    subprocess.run(['mysqldump', '-u', 'username', '-ppassword', 'rpdef', 'player', '--result-file=db.sql'])
