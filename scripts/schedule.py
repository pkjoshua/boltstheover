import requests
import sqlite3
import re
from datetime import datetime
import pytz

# Correct API URL for fetching schedule data
api_url = "http://api.sportradar.us/nhl/trial/v7/en/games/2023/REG/schedule.json?api_key=3s2jrxegxx8b7eqa6nay9898"
db_path = 'assets/data.db'

def fetch_schedule_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: HTTP {response.status_code}")
        return None

def utc_to_eastern(utc_str):
    """Convert UTC time string to Eastern Time string."""
    utc_time = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%SZ')
    eastern = pytz.timezone('US/Eastern')
    eastern_time = utc_time.replace(tzinfo=pytz.utc).astimezone(eastern)
    return eastern_time.strftime('%Y-%m-%d %H:%M:%S')

def extract_number(sr_id):
    """Extracts numerical part from sr_id string."""
    match = re.search(r'\d+', sr_id)
    return match.group(0) if match else sr_id

def insert_schedule_data(db_path, data):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    league_id = extract_number(data['league']['id'])
    season = data['season']['year']
    
    # Iterate through each game in the 'games' array
    for game in data['games']:
        global_event_id = game['id']
        status = game['status']
        date = game.get('scheduled', '')
        if date:
            date = utc_to_eastern(date)  # Using .get() in case 'scheduled' is missing
        home_points = game.get('home_points', 0)
        away_points = game.get('away_points', 0)
        event_id = extract_number(game.get('sr_id', ''))

        # Home team details
        home_id = game['home']['id']
        home_name = game['home']['name']
        home_alias = game['home']['alias']
        home_team_id = extract_number(game['home'].get('sr_id', ''))

        # Away team details
        away_id = game['away']['id']
        away_name = game['away']['name']
        away_alias = game['away']['alias']
        away_team_id = extract_number(game['away'].get('sr_id', ''))

        # Determine the winner
        if home_points > away_points:
            winner_team_id, winner_name = home_team_id, home_name
        elif away_points > home_points:
            winner_team_id, winner_name = away_team_id, away_name
        else:
            # Assumes the game hasn't been played yet or is a draw
            winner_team_id, winner_name = None, None

        # Insert data into the schedule table
        c.execute('''INSERT OR REPLACE INTO schedule (season_id, season, global_event_id, status, date, home_points, away_points,
                                           event_id, home_id, home_name, home_alias, home_team_id,
                                           away_id, away_name, away_alias, away_team_id, winner_team_id, winner_name)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (league_id, season, global_event_id, status, date, home_points, away_points,
                   event_id, home_id, home_name, home_alias, home_team_id,
                   away_id, away_name, away_alias, away_team_id, winner_team_id, winner_name))
    
    conn.commit()
    conn.close()

def main():
    schedule_data = fetch_schedule_data(api_url)
    if schedule_data:
        insert_schedule_data(db_path, schedule_data)
        print("Schedule data has been successfully inserted into the database.")
    else:
        print("No schedule data to insert.")

if __name__ == "__main__":
    main()
