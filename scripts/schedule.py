import requests
from bs4 import BeautifulSoup
import sqlite3
import os
import time

db_path = os.path.join('assets', 'data.db')

# Mapping of team URL segments to their IDs
team_ids = {
    "ana": "25", "ari": "24", "bos": "1", "buf": "2", "cgy": "3",
    "car": "7", "chi": "4", "col": "17", "cbj": "29", "dal": "9",
    "det": "5", "edm": "6", "fla": "26", "la": "8", "min": "30",
    "mtl": "10", "nsh": "27", "nj": "11", "nyi": "12", "nyr": "13",
    "ott": "14", "phi": "15", "pit": "16", "sj": "18", "sea": "124292",
    "stl": "19", "tb": "20", "tor": "21", "van": "22", "vgk": "37",
    "wsh": "23", "wpg": "28"
}

team_url_segments = [
    'ana/anaheim-ducks', 'ari/arizona-coyotes', 'bos/boston-bruins',
    'buf/buffalo-sabres', 'cgy/calgary-flames', 'car/carolina-hurricanes',
    'chi/chicago-blackhawks', 'col/colorado-avalanche', 'cbj/columbus-blue-jackets',
    'dal/dallas-stars', 'det/detroit-red-wings', 'edm/edmonton-oilers',
    'fla/florida-panthers', 'la/los-angeles-kings', 'min/minnesota-wild',
    'mtl/montreal-canadiens', 'nsh/nashville-predators', 'nj/new-jersey-devils',
    'nyi/new-york-islanders', 'nyr/new-york-rangers', 'ott/ottawa-senators',
    'phi/philadelphia-flyers', 'pit/pittsburgh-penguins', 'sj/san-jose-sharks',
    'sea/seattle-kraken', 'stl/st-louis-blues', 'tb/tampa-bay-lightning',
    'tor/toronto-maple-leafs', 'van/vancouver-canucks', 'vgk/vegas-golden-knights',
    'wsh/washington-capitals', 'wpg/winnipeg-jets'
]

def extract_team_abbreviation(href):
    # Extract the team abbreviation part of the URL
    parts = href.split('/')
    if len(parts) > 2:
        team_abbr = parts[-2]  # The abbreviation is the second last part of the URL
        return team_abbr.upper()  # Convert to uppercase to standardize
    return "UNK"  # Unknown team abbreviation

def fetch_schedule(team_url_segment, team_id):
    base_url = f'https://www.espn.com/nhl/team/schedule/_/name/{team_url_segment}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    schedule_rows = soup.find_all('tr', class_=['Table__TR Table__TR--sm Table__even', 'filled Table__TR Table__TR--sm Table__even'])

    schedule_data = []
    for row in schedule_rows:
        cols = row.find_all('td')
        if len(cols) >= 5:
            game_date = cols[0].text.strip()
            home_away = "Home" if "vs" in cols[1].text else "Away"
            opponent = cols[1].text.strip().replace('vs', '').replace('@', '').strip()

            game_link = cols[2].find('a', href=True)
            game_id = "N/A"
            if game_link and 'gameId' in game_link['href']:
                game_id = game_link['href'].split('gameId/')[1].split('/')[0]

            if len(cols) >= 6:
                # Extract result score and remove leading W/L
                full_result = cols[2].text.strip()
                result_score = ''.join([char for char in full_result if char.isdigit() or char == '-'])
                
                win_loss = cols[2].find('span', class_='fw-bold').text.strip() if cols[2].find('span', class_='fw-bold') else "N/A"
                record = cols[3].text.strip()
                goalie = cols[4].text.strip()
                top_performer = cols[5].text.strip()
            else:
                result_score = "NULL"
                win_loss = "NULL"
                record = "NULL"
                goalie = "NULL"
                top_performer = "NULL"

            schedule_data.append({
                'team_id': team_id,
                'date': game_date,
                'home_away': home_away,
                'opponent': opponent,
                'game_id': game_id,
                'win_loss': win_loss,
                'result_score': result_score,
                'record': record,
                'goalie': goalie,
                'top_performer': top_performer
            })

    return schedule_data

def insert_schedule_data_into_db(schedule_data):
    """Insert fetched schedule data into the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for game in schedule_data:
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO schedules (team_id, gameid, date, home_away, opponent, win_loss, result_score, record, goalie, top_performer)
            VALUES (:team_id, :game_id, :date, :home_away, :opponent, :win_loss, :result_score, :record, :goalie, :top_performer)
            ''', game)
        except sqlite3.IntegrityError as e:
            print(f"SQLite Integrity Error: {e}, for game ID: {game['game_id']}")
        except Exception as e:
            print(f"Unexpected error: {e}, for game ID: {game['game_id']}")

    conn.commit()
    conn.close()
    print("Schedule data successfully inserted into the database.")

all_schedule_data = []
for segment in team_url_segments:
    team_code = segment.split('/')[0]  # Extracts the team code
    team_id = team_ids.get(team_code, "Unknown")  # Fetch the team ID using the team code
    print(f"Fetching schedule for team ID {team_id}, Team Code {team_code}")
    team_schedule = fetch_schedule(segment, team_id)
    all_schedule_data.extend(team_schedule)
    time.sleep(1)  # Delay to prevent being flagged as a bot

insert_schedule_data_into_db(all_schedule_data)