import requests
import sqlite3
from datetime import datetime, timedelta
import pytz
import re
import time


# Configuration
db_path = 'assets/data.db'
api_key = '3s2jrxegxx8b7eqa6nay9898' 

# Two Teams!
teams = {
    'One': 3694,
    'Two': 3700,
}

# Fetch previous game data 
def fetch_previous_games(team_id):
    """Fetch the last 15 games for a given team before today's date."""
    today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date in the required format
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = """
        SELECT global_event_id
        FROM schedule
        WHERE (home_team_id = ? OR away_team_id = ?) AND date < ?
        ORDER BY date DESC
        LIMIT 15
        """
        c.execute(query, (team_id, team_id, today_date))  # Include today's date in the query
        games = c.fetchall()
        return [game[0] for game in games]

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
    print(f"Attempting to fetch data for game ID: {global_event_id}")
    url = f"http://api.sportradar.us/nhl/trial/v7/en/games/{global_event_id}/summary.json?api_key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch data for game {global_event_id}: HTTP {response.status_code}, skipping to next game.")
            return  # Skip this game and continue with the next one
        
        game_data = response.json()

        with sqlite3.connect(db_path) as conn:
            purge_existing_data_for_event(conn, global_event_id)
            
            c = conn.cursor()
            c.execute("SELECT date FROM schedule WHERE global_event_id = ?", (global_event_id,))
            date_row = c.fetchone()
            if date_row:
                date = date_row[0]  # Use the date from the schedule table
            else:
                print(f"No schedule entry found for global_event_id {global_event_id}, skipping to next game.")
                return  # Skip this game due to lack of schedule entry

            home_team_goals = game_data['home']['statistics']['total']['goals']
            away_team_goals = game_data['away']['statistics']['total']['goals']

            season = '2023-2024'  # Adjust based on logic or API data

            if home_team_goals > away_team_goals:
                home_result = "W"
                away_result = "L"
            elif home_team_goals < away_team_goals:
                home_result = "L"
                away_result = "W"
            else:
                home_result = "T"
                away_result = "T"

            for team_context in ['home', 'away']:
                team = game_data[team_context]
                opponent = game_data['away' if team_context == 'home' else 'home']
                home_away = team_context
                result = home_result if team_context == 'home' else away_result

                insert_team_stats(conn, global_event_id, game_data, team, opponent, season, date, home_away, result)

            print(f"Data successfully inserted for game {global_event_id}")
            
    except Exception as e:
        print(f"An error occurred while processing game {global_event_id}: {e}, skipping to next game.")

    finally:
        time.sleep(2) 

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
    for team_name, team_id in teams.items():
        print(f"Fetching previous games for {team_name}")
        previous_games_ids = fetch_previous_games(team_id)
        
        if not previous_games_ids:  # Check if the game IDs list is empty
            print(f"No games found for {team_name}.")
            continue  # Skip to the next team if no games found

        for global_event_id in previous_games_ids:
            print(f"Preparing to fetch stats for game ID: {global_event_id}")  # Log each game ID before the API call
            fetch_and_insert_team_stats(db_path, global_event_id, api_key)

if __name__ == "__main__":
    main()
