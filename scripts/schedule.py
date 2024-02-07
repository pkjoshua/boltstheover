import requests
from bs4 import BeautifulSoup
import csv
import time

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
    # Skip the header row
    schedule_rows = soup.find_all('tr', class_=['Table__TR Table__TR--sm Table__even', 'filled Table__TR Table__TR--sm Table__even'])[1:]

    schedule_data = []
    for row in schedule_rows:
        cols = row.find_all('td')
        if len(cols) >= 6:
            game_date = cols[0].text.strip()
            home_away = "Home" if "vs" in cols[1].text else "Away"
            opponent = cols[1].text.strip().replace('vs', '').replace('@', '').strip()

            result_link = cols[2].find('a', href=True)
            if result_link:
                game_id_link = result_link['href']
                game_id = game_id_link.split('gameId/')[1].split('/')[0]  # Extracts the numeric game ID
                result_score = result_link.text.strip()
            else:
                game_id = "N/A"
                result_score = "N/A"
            win_loss = cols[2].find('span', class_='fw-bold').text.strip() if cols[2].find('span', class_='fw-bold') else "N/A"

            record = cols[3].text.strip()
            goalie = cols[4].text.strip()
            top_performer = cols[5].text.strip()

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

def save_to_csv(data, file_name='nhl_schedules.csv'):
    headers = ['team_id', 'date', 'home_away', 'opponent', 'game_id', 'win_loss', 'result_score', 'record', 'goalie', 'top_performer']
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)
    print(f"Data successfully saved to {file_name}")

all_schedule_data = []
for segment in team_url_segments:
    team_code = segment.split('/')[0]  # Extracts the team code, e.g., 'ana' for Anaheim Ducks
    team_id = team_ids.get(team_code, "Unknown")  # Fetch the team ID using the team code
    print(f"Fetching schedule for team ID {team_id}, Team Code {team_code}")
    team_schedule = fetch_schedule(segment, team_id)
    all_schedule_data.extend(team_schedule)
    time.sleep(1)  # Delay to prevent being flagged as a bot

save_to_csv(all_schedule_data)