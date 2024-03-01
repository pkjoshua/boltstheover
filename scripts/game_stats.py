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

def get_latest_team_name_from_file():
    with open('team_name.txt', 'r') as f:
        team_name = f.read().strip()
    return team_name

def get_team_ids(team_names):
    """Fetch team_ids for given team names."""
    team_ids = {}
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        for name in team_names:
            c.execute("SELECT team_id, name FROM teams WHERE name = ?", (name,))
            result = c.fetchone()
            if result:
                team_ids[result[1]] = result[0]
            else:
                print(f"No team found for name: {name}")
    return team_ids

def find_next_game(team_ids):
    """Find the next game for each team based on the current date."""
    games = {}
    today_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        for name, team_id in team_ids.items():
            c.execute("""
                SELECT global_event_id, event_id, home_id, home_team_id, home_name, away_id, away_team_id, away_name
                FROM schedule
                WHERE date >= ? AND (home_team_id = ? OR away_team_id = ?)
                ORDER BY date ASC
                LIMIT 1
            """, (today_date, team_id, team_id))
            result = c.fetchone()
            if result:
                games[name] = {
                    'global_event_id': result[0],
                    'event_id': result[1],
                    'home_id': result[2],
                    'home_team_id': result[3],
                    'home_name': result[4],
                    'away_id': result[5],
                    'away_team_id': result[6],
                    'away_name': result[7],
                }
            else:
                print(f"No upcoming games found for team: {name}")
    return games

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
            return

        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f"Failed to fetch data for game {global_event_id}: HTTP {response.status_code}, skipping to next game.")
                return
            
            game_data = response.json()
                
            c = conn.cursor()
            c.execute("SELECT date FROM schedule WHERE global_event_id = ?", (global_event_id,))
            date_row = c.fetchone()
            if date_row:
                date = date_row[0]
            else:
                print(f"No schedule entry found for global_event_id {global_event_id}, skipping to next game.")
                return
            
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
                # Check for shootout goals to determine the winner
                home_shootout_goals = game_data['home'].get('shootout', {}).get('goals', 0)
                away_shootout_goals = game_data['away'].get('shootout', {}).get('goals', 0)
                if home_shootout_goals > away_shootout_goals:
                    home_result = "W"
                    away_result = "L"
                elif home_shootout_goals < away_shootout_goals:
                    home_result = "L"
                    away_result = "W"
                else:
                    home_result = "?"
                    away_result = "?"
                    print("Unable to determine winner based on shootout data.")
                    return

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
    logging.basicConfig(level=logging.INFO)
    logging.info("Script started")
    
    # Fetch the latest team name from file
    team_name = get_latest_team_name_from_file()
    team_names = [team_name]  # Prepare for potentially getting multiple team names
    
    # Fetch team IDs for the team names
    team_ids = get_team_ids(team_names)
    
    # Find the next game for the team(s)
    next_games = find_next_game(team_ids)
    
    for name, game_info in next_games.items():
        logging.info(f"Processing next game for team: {name}")
        
        # Process both teams involved in the next game
        home_team_id = game_info['home_team_id']
        away_team_id = game_info['away_team_id']
        
        for team_id in [home_team_id, away_team_id]:
            logging.info(f"Fetching and inserting stats for team ID: {team_id}")
            # This function call might need to be adjusted based on its implementation details
            fetch_and_insert_team_stats(db_path, game_info['event_id'], api_key)
        
        # Process previous games for both teams
        for team_id in [home_team_id, away_team_id]:
            logging.debug(f"Fetching previous games for team ID: {team_id}")
            previous_games_ids = fetch_previous_games(team_id)
            
            if not previous_games_ids:
                logging.info(f"No previous games found for team ID: {team_id}, skipping.")
                continue

            for global_event_id in previous_games_ids:
                logging.debug(f"Fetching and inserting stats for game ID: {global_event_id}")
                fetch_and_insert_team_stats(db_path, global_event_id, api_key)
    
    logging.info("Script completed")

if __name__ == "__main__":
    main()