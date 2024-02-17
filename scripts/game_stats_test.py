import requests
import sqlite3
from datetime import datetime
import pytz
import re

# Configuration
db_path = 'assets/data.db'
api_key = '3s2jrxegxx8b7eqa6nay9898'  # Replace with your actual API key
global_event_id = '34ea38e0-b59c-4cae-9be0-ebd29a57f54a'  # Replace with your actual event ID

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

def fetch_and_insert_team_stats(db_path, global_event_id, api_key):
    url = f"http://api.sportradar.us/nhl/trial/v7/en/games/{global_event_id}/summary.json?api_key={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data for game {global_event_id}: HTTP {response.status_code}")
        return

    game_data = response.json()

    with sqlite3.connect(db_path) as conn:
        # First, purge existing data for this event
        purge_existing_data_for_event(conn, global_event_id)
        
        # Fetch the game date from the schedule table
        c = conn.cursor()
        c.execute("SELECT date FROM schedule WHERE global_event_id = ?", (global_event_id,))
        date_row = c.fetchone()
        if date_row:
            date = date_row[0]  # Use the date from the schedule table
        else:
            print(f"No schedule entry found for global_event_id {global_event_id}.")
            return  # Exit the function early if no date is found

        home_team_goals = game_data['home']['statistics']['total']['goals']
        away_team_goals = game_data['away']['statistics']['total']['goals']

        # Assuming the season needs to be derived or fixed, adjust this as necessary
        season = '2023-2024'  # This could be dynamic based on your application's logic

        # Determine the result based on goals
        if home_team_goals > away_team_goals:
            home_result = "W"
            away_result = "L"
        elif home_team_goals < away_team_goals:
            home_result = "L"
            away_result = "W"
        else:
            home_result = "T"
            away_result = "T"

        # Process and insert data for both teams
        for team_context in ['home', 'away']:
            team = game_data[team_context]
            opponent = game_data['away' if team_context == 'home' else 'home']
            home_away = team_context
            result = home_result if team_context == 'home' else away_result

            # Insert the team data with the updated logic for statistics and winning determination
            insert_team_stats(conn, global_event_id, game_data, team, opponent, season, date, home_away, result)

        print(f"Data inserted for game {global_event_id}")

def purge_existing_data_for_event(conn, global_event_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM team_stats_per_game WHERE global_event_id = ?", (global_event_id,))
    conn.commit()
    print(f"Purged existing data for global_event_id {global_event_id}")

def insert_team_stats(conn, global_event_id, game_data, team, opponent, season, date, home_away, result):
    cursor = conn.cursor()

    # Extract statistics from the provided structure
    stats = team['statistics']['total']
    
    # Use the extract_number function on sr_id fields
    team_sr_id = extract_number(team.get('sr_id', ''))
    opponent_sr_id = extract_number(opponent.get('sr_id', ''))

    # Adjusted data tuple to include actual statistics extracted from the API response
    data = (global_event_id, game_data.get('sr_id', ''), team['id'], team_sr_id, team['name'],
            opponent['id'], opponent_sr_id, opponent['name'],
            season, date, home_away, result,
            stats.get('goals', 0), stats.get('assists', 0), stats.get('penalties', 0), stats.get('penalty_minutes', 0), 
            stats.get('shots', 0), stats.get('blocked_att', 0), stats.get('missed_shots', 0), stats.get('hits', 0), 
            stats.get('giveaways', 0), stats.get('takeaways', 0), stats.get('blocked_shots', 0), stats.get('faceoffs_won', 0), 
            stats.get('faceoffs_lost', 0), stats.get('powerplays', 0), stats.get('points', 0))

    cursor.execute('''
        INSERT INTO team_stats_per_game (global_event_id, event_id, global_team_id, team_id, name, 
            global_opponent_id, opponent_id, opponent_name, season, date, home_away, result, 
            goals, assists, penalties, penalty_minutes, shots, blocked_att, missed_shots, hits, 
            giveaways, takeaways, blocked_shots, faceoffs_won, faceoffs_lost, 
            powerplays, points) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', data)

    conn.commit()

def main():
    fetch_and_insert_team_stats(db_path, global_event_id, api_key)

if __name__ == "__main__":
    main()