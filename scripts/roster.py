import requests
from bs4 import BeautifulSoup
import csv
import time
import os
import sqlite3

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

# Position abbreviations
position_map = {
    'Centers': 'C',
    'Left Wings': 'LW',
    'Right Wings': 'RW',
    'Defense': 'D',
    'Goalies': 'G'
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

db_path = os.path.join('assets', 'data.db')

def fetch_roster_data(team_url_segment, team_id):
    base_url = f'https://www.espn.com/nhl/team/roster/_/name/{team_url_segment}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    current_position = "Unknown"
    players_data = []

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    roster_elements = soup.find_all(['tr', 'div'], class_=['Table__TR Table__TR--lg Table__even', 'Table__Title'])

    for element in roster_elements:
        if element.name == 'div' and 'Table__Title' in element['class']:
            current_position = position_map.get(element.text.strip(), "Unknown")
        elif element.name == 'tr':
            cols = element.find_all('td')
            if cols:
                player_link = cols[1].find('a')['href'] if cols[1].find('a') else ''
                player_id = player_link.split('/')[-1] if player_link else 'N/A'
                player_info = {
                    'team_id': team_id,
                    'player_id': player_id,
                    'name': cols[1].find('a').text.strip() if cols[1].find('a') else 'Unknown',
                    'jersey_number': cols[1].find('span').text.strip() if cols[1].find('span') else 'N/A',
                    'age': cols[2].text.strip(),
                    'height': cols[3].text.strip(),
                    'weight': cols[4].text.strip(),
                    'shot': cols[5].text.strip(),
                    'position': current_position
                }
                players_data.append(player_info)

    return players_data

def insert_roster_data(players_data):
    """Insert roster data into the SQLite database."""
    conn = sqlite3.connect(db_path)  # Connect to your SQLite database
    cursor = conn.cursor()

    for player in players_data:
        try:
            # Insert or replace existing record
            cursor.execute('''
            INSERT OR REPLACE INTO roster (team_id, player_id, name, jersey_number, age, height, weight, shot, position)
            VALUES (:team_id, :player_id, :name, :jersey_number, :age, :height, :weight, :shot, :position)
            ''', player)
        except sqlite3.IntegrityError as e:
            print(f"SQLite Integrity Error: {e}, for player: {player['name']}")
        except Exception as e:
            print(f"Unexpected error: {e}, for player: {player['name']}")

    conn.commit()  # Commit the transaction
    conn.close()  # Close the connection
    print("Roster data successfully inserted into the database.")

all_players_data = []
for team_url_segment in team_url_segments:
    team_code = team_url_segment.split('/')[0]  # Extracts the team code
    team_id = team_ids.get(team_code, "Unknown")  # Fetch the team ID using the team code
    print(f"Fetching data for team ID {team_id}, team code {team_code}")
    players_data = fetch_roster_data(team_url_segment, team_id)
    all_players_data.extend(players_data)
    time.sleep(1)  # Delay to prevent being flagged as a bot

# Insert the fetched data into the database
insert_roster_data(all_players_data)


