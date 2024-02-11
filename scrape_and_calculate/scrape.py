from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_headers import Headers
import requests

def get_pbp_stats(season):
    URL = "https://api.pbpstats.com/get-totals/nba?Season=" + season + "&SeasonType=Regular%2BSeason&Type=Player"

    r = requests.get(url=URL)

    # extracting data in json format
    data = r.json()['multi_row_table_data']
    relevant_stats = {}
    for record in data:
        games_played = record['GamesPlayed']
        mpg = record['Minutes']/games_played
        if 'Steals' in record:
            steals = record['Steals']/games_played
        else:
            steals = 0
        if 'Blocks' in record:
            if 'BlockedAtRim' in record:
                blocks_rim = record['BlockedAtRim'] / games_played
                blocks_perimeter = (record['Blocks'] - record['BlockedAtRim']) / games_played
            else:
                blocks_perimeter = record['Blocks']/games_played
        else:
            blocks_perimeter = 0
            blocks_rim = 0
        if 'Charge Fouls Drawn' in record:
            charges = record['Charge Fouls Drawn']/games_played
        else:
            charges = 0
        relevant_stats[record['Name']] = [mpg, steals, blocks_perimeter, charges, mpg, blocks_rim]
    return relevant_stats

def traditional_stats(season):
    url = 'https://www.nba.com/stats/players/traditional?Season=' + season

    driver = get_web_driver()

    driver.get(url)

    # Wait for the table to load
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'DropDown_select__4pIg9')))
    except:
        with open('error_page_source.txt', 'w') as f:
            f.write(driver.page_source)

    selects = driver.find_elements(By.CLASS_NAME, "DropDown_select__4pIg9   ")
    for select in selects:
        options = Select(select).options

    for option in options:
        if option.text == 'All':
            option.click() # select() in earlier versions of webdriver
            break

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Crom_table__p1iZz')))
    except:
        with open('error_page_source.txt', 'w') as f:
            f.write(driver.page_source)

    # Find the table element
    table = driver.find_element(By.CLASS_NAME, 'Crom_table__p1iZz')

    # Find all rows in the table
    rows = table.find_elements(By.TAG_NAME, 'tr')
    traditional_stats = []
    # Loop through each row and extract the data from each cell
    num = 0
    for row in rows:
        player_stats = []
        i=0
        # Find all cells in the row
        cells = row.find_elements(By.TAG_NAME, 'td')
        for cell in cells:
            if i != 0 and i != 5 and i != 6 and i != 26 and i != 27 and i != 28:
                player_stats.append(cell.text)
            i+=1
        if num != 0:
            traditional_stats.append(player_stats)
        num+=1

    header = ['Player', 'Team', 'Age', 'GP', 'MIN', 'PTS', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%',
                  "FTM", "FTA", "FT%", "OREB", "DREB", "REB", "AST", "TOV", "STL", "BLK", "PF", "+/-"]
    return header, traditional_stats

def team_defenses(season):
    url = 'https://www.nba.com/stats/teams/defense?Season=' + season
  
    driver = get_web_driver()

    driver.get(url)

    # Wait for the table to load, if it doesn't load display content
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Crom_table__p1iZz')))
    except:
        with open('error_page_source.txt', 'w') as f:
            f.write(driver.page_source)

    # Find the table element
    table = driver.find_element(By.CLASS_NAME, 'Crom_table__p1iZz')

    # Find all rows in the table
    rows = table.find_elements(By.TAG_NAME, 'tr')
    team_defenses = []
    # Loop through each row and extract the data from each cell
    for row in rows:
        i=0
        # Find all cells in the row
        cells = row.find_elements(By.TAG_NAME, 'td')
        team=''
        def_rtg = 0
        opp_pts_paint = 0
        for cell in cells:
            if i==1:
                team = cell.text
            elif i==6:
                def_rtg = float(cell.text)
            elif i==14:
                opp_pts_paint = float(cell.text)
            i+=1
        if team:
            team_defenses.append([get_team_abbrivation(team), def_rtg, opp_pts_paint])
    header = ['Team', 'DEF', 'RDEF']
    return header, team_defenses

def get_team_abbrivation(fullname):
    if fullname == "Milwaukee Bucks":
        return "MIL"
    elif fullname == "Boston Celtics":
        return "BOS"
    elif fullname == "Denver Nuggets":
        return "DEN"
    elif fullname == "Philadelphia 76ers":
        return "PHI"
    elif fullname == "Cleveland Cavaliers":
        return "CLE"
    elif fullname == "Memphis Grizzlies":
        return "MEM"
    elif fullname == "New York Knicks":
        return "NYK"
    elif fullname == "Sacramento Kings":
        return "SAC"
    elif fullname == "Brooklyn Nets":
        return "BKN"
    elif fullname == "Phoenix Suns":
        return "PHX"
    elif fullname == "Miami Heat":
        return "MIA"
    elif fullname == "LA Clippers":
        return "LAC"
    elif fullname == "Los Angeles Clippers":
        return "LAC"
    elif fullname == "Atlanta Hawks":
        return "ATL"
    elif fullname == "Dallas Mavericks":
        return "DAL"
    elif fullname == "Golden State Warriors":
        return "GSW"
    elif fullname == "Minnesota Timberwolves":
        return "MIN"
    elif fullname == "Los Angeles Lakers":
        return "LAL"
    elif fullname == "New Orleans Pelicans":
        return "NOP"
    elif fullname == "Toronto Raptors":
        return "TOR"
    elif fullname == "Utah Jazz":
        return "UTA"
    elif fullname == "Oklahoma City Thunder":
        return "OKC"
    elif fullname == "Portland Trail Blazers":
        return "POR"
    elif fullname == "Washington Wizards":
        return "WAS"
    elif fullname == "Chicago Bulls":
        return "CHI"
    elif fullname == "Indiana Pacers":
        return "IND"
    elif fullname == "Orlando Magic":
        return "ORL"
    elif fullname == "Charlotte Hornets":
        return "CHA"
    elif fullname == "Charlotte Bobcats":
        return "CHA"
    elif fullname == "San Antonio Spurs":
        return "SAS"
    elif fullname == "Detroit Pistons":
        return "DET"
    elif fullname == "Houston Rockets":
        return "HOU"

def defense_dash_overall(pbp_stats, season):
    # Defense dash for greater than 15
    url = 'https://www.nba.com/stats/players/defense-dash-overall?Season=' + season

    driver = get_web_driver()

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'DropDown_select__4pIg9')))
    except:
        with open('error_page_source.txt', 'w') as f:
            f.write(driver.page_source)

    selects = driver.find_elements(By.CLASS_NAME, "DropDown_select__4pIg9 ")
    for select in selects:
        options = Select(select).options

    for option in options:
        if option.text == 'All':
            option.click() # select() in earlier versions of webdriver
            break
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Crom_table__p1iZz')))
    except:
        with open('error_page_source.txt', 'w') as f:
            f.write(driver.page_source)

    # Find the table element
    table = driver.find_element(By.CLASS_NAME, 'Crom_table__p1iZz')

    # Find all rows in the table
    rows = table.find_elements(By.TAG_NAME, 'tr')
    defense_dash_overall = []
    # Loop through each row and extract the data from each cell
    for row in rows:
        player_dd_overall = []
        # Find all cells in the row
        cells = row.find_elements(By.TAG_NAME, 'td')
        for cell in cells:
            player_dd_overall.append(cell.text)
        # Add pbp stats to defense_dash if not empty
        if player_dd_overall:
            if player_dd_overall[0] in pbp_stats:
                defense_dash_overall.append(player_dd_overall + pbp_stats[player_dd_overall[0]][:4])
            else:
                defense_dash_overall.append(player_dd_overall + ['NaN', 'NaN', 'NaN', 'NaN'])

    header = ['Player', 'Team', 'Age', 'Position', 'GP', 'Games', 'FREQ%', 'DFGM', 'DFGA', 'DFG%', 'FG%', 'DIFF%', "MP", "STL", "BLKP", "Charges"]
    return header, defense_dash_overall

def defense_dash_lt10(pbp_stats, season):
    # Less than 10 foot
    url = 'https://www.nba.com/stats/players/defense-dash-lt10?Season=' + season

    driver = get_web_driver()

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'DropDown_select__4pIg9')))
    except:
        with open('error_page_source.txt', 'w') as f:
            f.write(driver.page_source)

    selects = driver.find_elements(By.CLASS_NAME, "DropDown_select__4pIg9 ")
    for select in selects:
        options = Select(select).options

    for option in options:
        if option.text == 'All':
            option.click() # select() in earlier versions of webdriver
            break

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'Crom_table__p1iZz')))
    except:
        with open('error_page_source.txt', 'w') as f:
            f.write(driver.page_source)

    # Find the table element
    table = driver.find_element(By.CLASS_NAME, 'Crom_table__p1iZz')

    # Find all rows in the table
    rows = table.find_elements(By.TAG_NAME, 'tr')
    defense_dash_lt10 = []

    # Loop through each row and extract the data from each cell
    for row in rows:
        player_dd_lt10 = []
        # Find all cells in the row
        cells = row.find_elements(By.TAG_NAME, 'td')
        for cell in cells:
                player_dd_lt10.append(cell.text)
        # Add pbp stats to defense dash if not empty
        if player_dd_lt10:
            if player_dd_lt10[0] in pbp_stats:
                defense_dash_lt10.append(player_dd_lt10 + pbp_stats[player_dd_lt10[0]][-2:])
            else:
                defense_dash_lt10.append(player_dd_lt10 + ['NaN', 'NaN'])
    header = ['Player', 'Team', 'Age', 'Position', 'GP', 'Games', 'FREQ%', 'DFGM', 'DFGA', 'DFG%', 'FG%', 'DIFF%', "MP", "BLKR"]
    return header, defense_dash_lt10

def get_driver_options():
    header = Headers(
        browser="chrome",  # Generate only Chrome UA
        os="win",  # Generate only Windows platform
        headers=False # generate misc headers
    )
    options = Options()
    options.add_argument('--headless')  # Runs Chrome in headless mode.
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    customUserAgent = header.generate()['User-Agent']
    options.add_argument(f"user-agent={customUserAgent}")
    return options

def get_web_driver():
    #driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=get_driver_options())
    driver = webdriver.Chrome("/usr/bin/chromedriver", options=get_driver_options())
    return driver