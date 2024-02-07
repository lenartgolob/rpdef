import pandas as pd
import statistics
from nba_api.stats.endpoints import leaguegamefinder
import numpy as np

def calculate_diff_percentage(num, lower_limit, upper_limit):
    return (upper_limit-num)/(upper_limit-lower_limit)

def team_defenses_coefficient(header, team_defenses):
    team_defenses = pd.DataFrame(team_defenses, columns=header)

    pdef = team_defenses.sort_values('DEF')['DEF'].values
    min_pdef = pdef[0]
    max_pdef = pdef[len(pdef) - 1]

    rdef = team_defenses.sort_values('RDEF')['RDEF'].values
    min_rdef = rdef[0]
    max_rdef = rdef[len(pdef) - 1]

    team_defenses_coefficient = {}
    for index, row in team_defenses.iterrows():
        team_defenses_coefficient[row['Team']] = (calculate_diff_percentage(row['DEF'], min_pdef, max_pdef)*0.5+0.75,
            calculate_diff_percentage(row['RDEF'], min_rdef, max_rdef)*0.5+0.75)
    return team_defenses_coefficient

def get_players_positions(header, defense_dash_lt10):
    defense_dash_lt10 = pd.DataFrame(defense_dash_lt10, columns=header)
    #defense_dash_lt10 = defense_dash_lt10[pd.notna(defense_dash_lt10.MP)]
    player_positions = {}
    for index, row in defense_dash_lt10.iterrows():
        if row['Player'] not in player_positions:
            player_positions[row['Player']] = row['Position']
    return player_positions

def player_stops_lt10(lt10):
    diff = lt10.sort_values('DIFF%')['DIFF%'].values
    best_diff = diff[0]
    worst_diff = diff[len(diff) - 1]
    dfg = lt10.sort_values('DFG%')['DFG%'].values
    best_dfg = dfg[0]
    worst_dfg = dfg[len(diff) - 1]
    players_stops = {}
    for index, row in lt10.iterrows():
        stop1 = row['BLKR']
        stop2 = (calculate_diff_percentage(row['DIFF%'], best_diff, worst_diff)*0.5+0.75) * \
                (calculate_diff_percentage(row['DFG%'], best_dfg, worst_dfg)*0.5+0.75)
        players_stops[row['Player']] = [0.5*stop1 + stop2, row['Team'], stop1, stop2]
    return players_stops

def teams_total_stops(stops):
    team_total_stops = {}
    for player, value in stops.items():
        stop = value[0]
        team = value[1]
        if team not in team_total_stops:
            team_total_stops[team] = [stop]
        else:
            team_total_stops[team].append(stop)
    return team_total_stops

def final_rating(stops, team_total_stops, team_defenses_coefficient, traded_players, gt10):
    for player, value in stops.items():
        if player in traded_players:
            player_contribution = 0
            stop = value[0]
            total_games_played = sum(traded_players[player].values())
            team_defense = 0
            for team, games_num in traded_players[player].items():
                average_team_stops = statistics.mean(team_total_stops[team])
                player_contribution += (stop/average_team_stops) * (games_num/total_games_played)
                if gt10:
                    team_defense += team_defenses_coefficient[team][0]*(games_num/total_games_played)
                else:
                    team_defense += team_defenses_coefficient[team][1]*(games_num/total_games_played)
            player_team = player_contribution * team_defense
            final_rating = stop + player_team
            stops[player].extend([average_team_stops, player_contribution, team_defense, player_team, final_rating])
        else:
            stop = value[0]
            team = value[1]
            average_team_stops = statistics.mean(team_total_stops[team])
            # Player ranking based on how much he contributes to his team, compare him to average
            player_contribution = stop / average_team_stops
            if gt10:
                team_defense = team_defenses_coefficient[team][0]
            else:
                team_defense = team_defenses_coefficient[team][1]
            player_team = player_contribution * team_defense
            final_rating = stop + player_team
            # Collect all data
            # stop, team, stop1, stop2, player_team_rating, team_pdef_coefficient, final_pdef
            stops[player].extend([average_team_stops, player_contribution, team_defense, player_team, final_rating])
    return stops

def defense_dash_lt10(header, defense_dash_lt10):
    defense_dash_lt10 = pd.DataFrame(defense_dash_lt10, columns=header)
    # Removes NaN values and converts to numeric
    defense_dash_lt10['MP'] = pd.to_numeric(defense_dash_lt10['MP'], errors='coerce')
    defense_dash_lt10 = defense_dash_lt10[pd.notna(defense_dash_lt10.MP)]
    defense_dash_lt10['GP'] = pd.to_numeric(defense_dash_lt10['GP'], errors='coerce')
    defense_dash_lt10 = defense_dash_lt10[pd.notna(defense_dash_lt10.GP)]

    defense_dash_lt10['DFGM'] = pd.to_numeric(defense_dash_lt10['DFGM'], errors='coerce')
    defense_dash_lt10['DFGA'] = pd.to_numeric(defense_dash_lt10['DFGA'], errors='coerce')
    defense_dash_lt10['DFG%'] = pd.to_numeric(defense_dash_lt10['DFG%'], errors='coerce')
    defense_dash_lt10['FG%'] = pd.to_numeric(defense_dash_lt10['FG%'], errors='coerce')
    defense_dash_lt10['DIFF%'] = pd.to_numeric(defense_dash_lt10['DIFF%'], errors='coerce')
    defense_dash_lt10['BLKR'] = pd.to_numeric(defense_dash_lt10['BLKR'], errors='coerce')

    # Removes outliers from defense_dash_lt10
    defense_dash_lt10 = defense_dash_lt10[defense_dash_lt10.MP > 18]
    defense_dash_lt10 = defense_dash_lt10[defense_dash_lt10.GP > 15]
    return defense_dash_lt10

def defense_dash_overall(header, defense_dash_overall):
    defense_dash_overall = pd.DataFrame(defense_dash_overall, columns=header)
    # Removes NaN values and converts to numeric
    defense_dash_overall['MP'] = pd.to_numeric(defense_dash_overall['MP'], errors='coerce')
    defense_dash_overall = defense_dash_overall[pd.notna(defense_dash_overall.MP)]
    defense_dash_overall['GP'] = pd.to_numeric(defense_dash_overall['GP'], errors='coerce')
    defense_dash_overall = defense_dash_overall[pd.notna(defense_dash_overall.GP)]

    defense_dash_overall['DFGM'] = pd.to_numeric(defense_dash_overall['DFGM'], errors='coerce')
    defense_dash_overall['DFGA'] = pd.to_numeric(defense_dash_overall['DFGA'], errors='coerce')
    defense_dash_overall['DFG%'] = pd.to_numeric(defense_dash_overall['DFG%'], errors='coerce')
    defense_dash_overall['FG%'] = pd.to_numeric(defense_dash_overall['FG%'], errors='coerce')
    defense_dash_overall['DIFF%'] = pd.to_numeric(defense_dash_overall['DIFF%'], errors='coerce')
    defense_dash_overall['BLKP'] = pd.to_numeric(defense_dash_overall['BLKP'], errors='coerce')
    # Removes outliers from defense_dash_overall
    defense_dash_overall = defense_dash_overall[pd.notna(defense_dash_overall.MP)]
    defense_dash_overall = defense_dash_overall[defense_dash_overall.MP > 18]
    defense_dash_overall = defense_dash_overall[defense_dash_overall.GP > 15]
    return defense_dash_overall

def player_stops_gt10(lt10, overall):
    dd_lt10 = {}
    dd_gt10 = {}
    for index, row in lt10.iterrows():
        dd_lt10[row['Player']] = (row['DFGM'], row['DFGA'])

    for index, row in overall.iterrows():
        player = row['Player']
        if player in dd_lt10:
            dfgm = row['DFGM']-dd_lt10[player][0]
            dfga = row['DFGA']-dd_lt10[player][1]
            dfg = (dfgm/dfga)*100
            dd_gt10[player] = dfg

    key_max = max(dd_gt10.keys(), key=(lambda k: dd_gt10[k]))
    key_min = min(dd_gt10.keys(), key=(lambda k: dd_gt10[k]))
    min_dfg = dd_gt10[key_min]
    max_dfg = dd_gt10[key_max]
    players_stops = {}

    for index, row in overall.iterrows():
        stop1 = row['STL'] + row['BLKP'] + row['Charges']
        stop2 = calculate_diff_percentage(dd_gt10[row['Player']], min_dfg, max_dfg)*0.5+0.75
        players_stops[row['Player']] = [0.25*stop1 + stop2, row['Team'], stop1, stop2]
    return players_stops

def traditional_stats(header, traditional_stats):
    traditional = pd.DataFrame(traditional_stats, columns=header)
    return traditional

def traded_players(lt10, season):
    # Set the season year and team abbreviation
    players_teams = {}
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=None,
                                                   player_id_nullable=None,
                                                   season_nullable=season,
                                                   season_type_nullable='Regular Season',
                                                   league_id_nullable='00',
                                                   player_or_team_abbreviation='P')

    games = gamefinder.get_data_frames()[0]
    for player_name in lt10.keys():
        player_teams = {}
        player_games = games[games.PLAYER_NAME == player_name]
        arr = player_games['TEAM_ABBREVIATION'].values
        unique_vals = np.unique(arr)
        if len(unique_vals) > 1:
            # Count occurrences of each value in array
            for val in unique_vals:
                count = np.count_nonzero(arr == val)
                player_teams[val] = count
            players_teams[player_name] = player_teams
    return players_teams
