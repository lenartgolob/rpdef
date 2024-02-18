import scrape
import calculate
import database

season = "2023-24"

pbp_stats = scrape.get_pbp_stats(season)
header, teams_defense = scrape.team_defenses(season)
teams_defense_coefficient = calculate.team_defenses_coefficient(header, teams_defense)

header_lt10, defense_dash_lt10 = scrape.defense_dash_lt10(pbp_stats, season)
lt10 = calculate.defense_dash_lt10(header_lt10, defense_dash_lt10)
lt10_stops = calculate.player_stops_lt10(lt10)
traded_players = calculate.traded_players(lt10_stops, season)
team_total_stops = calculate.teams_total_stops(lt10_stops)
lt10_rating = calculate.final_rating(lt10_stops, team_total_stops, teams_defense_coefficient, traded_players, False)

header, defense_dash_overall = scrape.defense_dash_overall(pbp_stats, season)
overall = calculate.defense_dash_overall(header, defense_dash_overall)
gt10_stops = calculate.player_stops_gt10(lt10, overall)
team_total_stops = calculate.teams_total_stops(gt10_stops)
gt10_rating = calculate.final_rating(gt10_stops, team_total_stops, teams_defense_coefficient, traded_players, True)


player_positions = calculate.get_players_positions(header_lt10, defense_dash_lt10)
header, traditional_stats = scrape.traditional_stats(season)
traditional = calculate.traditional_stats(header, traditional_stats)

database.update(traditional, lt10_rating, gt10_rating, player_positions, season)