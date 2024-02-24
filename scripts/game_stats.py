import requests
import sqlite3
from datetime import datetime, timedelta
import pytz
import re
import time
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
db_path = 'assets/data.db'
api_key = '3s2jrxegxx8b7eqa6nay9898' 

# Teams by name
teams = ['Devils', 'Lightning']

def get_team_id_from_name(team_name):
    """Retrieve team ID from the database based on team name."""
    logging.debug(f"Attempting to get team ID for: {team_name}")
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT team_id FROM teams WHERE name = ? LIMIT 1"
        cursor.execute(query, (team_name,))
        result = cursor.fetchone()
        if result:
            logging.debug(f"Found team ID {result[0]} for team name: {team_name}")
            return result[0]
        else:
            logging.warning(f"No team found for name: {team_name}")
            return None

def data_exists_for_event(conn, global_event_id):
    """Check if data for the global_event_id already exists."""
    cursor = conn.cursor()
    cursor.execute("SELECT EXISTS(SELECT 1 FROM team_stats_per_game WHERE global_event_id = ? LIMIT 1)", (global_event_id,))
    return cursor.fetchone()[0]

# Fetch previous game data 
def fetch_previous_games(team_id):
    """Fetch the previous games for a given team before today's date."""
    today_date = datetime.now().strftime('%Y-%m-%d')  # Get today's date in the required format
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = """
        SELECT global_event_id
        FROM schedule
        WHERE (home_team_id = ? OR away_team_id = ?) AND date < ?
        ORDER BY date DESC
        LIMIT 100
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
    
    with sqlite3.connect(db_path) as conn:
        if data_exists_for_event(conn, global_event_id):
            print(f"Data already exists for game {global_event_id}, skipping.")
            return  # Skip this game as data already exists

        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch data for game {global_event_id}: HTTP {response.status_code}, skipping to next game.")
                return  # Skip this game and continue with the next one
            
            game_data = response.json()
                
            c = conn.cursor()
            c.execute("SELECT date FROM schedule WHERE global_event_id = ?", (global_event_id,))
            date_row = c.fetchone()
            if date_row:
                date = date_row[0]  # Use the date from the schedule table
            else:
                print(f"No schedule entry found for global_event_id {global_event_id}, skipping to next game.")
                return  # Skip this game due to lack of schedule entry
            
            # This block must be outside the else clause above
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
    try:
        cursor.execute('''
            INSERT INTO team_stats_per_game (global_event_id, event_id, global_team_id, team_id, name, 
                global_opponent_id, opponent_id, opponent_name, season, date, home_away, result, 
                goals, assists, penalties, penalty_minutes, shots, blocked_att, missed_shots, hits, 
                giveaways, takeaways, blocked_shots, faceoffs_won, faceoffs_lost, 
                powerplays, points) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)

        conn.commit()
        print(f"Data successfully inserted for team {team['name']} in game {global_event_id}")
    except Exception as e:
        print(f"Failed to insert data for team {team['name']} in game {global_event_id}: {e}")


def main():
    logging.info("Script started")
    for team_name in teams:
        logging.info(f"Processing team: {team_name}")
        team_id = get_team_id_from_name(team_name)
        
        if team_id is None:
            logging.error(f"Failed to get team ID for {team_name}, skipping.")
            continue
        
        logging.debug(f"Fetching previous games for team ID: {team_id}")
        previous_games_ids = fetch_previous_games(team_id)
        
        if not previous_games_ids:
            logging.info(f"No previous games found for {team_name}, skipping.")
            continue

        for global_event_id in previous_games_ids:
            logging.debug(f"Fetching and inserting stats for game ID: {global_event_id}")
            fetch_and_insert_team_stats(db_path, global_event_id, api_key)
    
    logging.info("Script completed")

if __name__ == "__main__":
    main()