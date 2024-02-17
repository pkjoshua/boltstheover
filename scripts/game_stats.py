import requests
import sqlite3

db_path = 'assets/data.db'
api_key = '3s2jrxegxx8b7eqa6nay9898'

def get_games_to_fetch(db_path):
    """Fetch games from the schedule that need team stats."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT global_event_id FROM schedule WHERE NOT EXISTS (SELECT 1 FROM team_stats_per_game WHERE team_stats_per_game.global_event_id = schedule.global_event_id)")
        games = cursor.fetchall()
    return [game[0] for game in games]

def fetch_and_insert_team_stats(db_path, global_event_id, api_key):
    url = f"http://api.sportradar.us/nhl/trial/v7/en/games/{global_event_id}/summary.json?api_key={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data for game {global_event_id}")
        return

    data = response.json()
    insert_team_stats(db_path, data)

def insert_team_stats(db_path, game_data):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Extract common data
        global_event_id = game_data['id']
        event_id = game_data['sr_id']
        date = game_data['scheduled']
        season = '2021-2022'  # Example, adjust based on your logic
        
        for team_context in ['home', 'away']:
            team = game_data[team_context]
            opponent = game_data['away' if team_context == 'home' else 'home']
            
            # Check if data already exists
            cursor.execute("SELECT 1 FROM team_stats_per_game WHERE global_event_id = ? AND global_team_id = ?", (global_event_id, team['id']))
            if cursor.fetchone():
                continue  # Skip if entry already exists
            
            # Prepare data for insertion
            data = (global_event_id, event_id, team['id'], team['sr_id'], team['name'], opponent['id'], opponent['sr_id'], opponent['name'],
                    season, date, team_context, '',  # Result and other stats to be filled as per available data
                    team['goals'], team['assists'], team['penalties'], team['penalty_minutes'], team['shots'], 0,  # Placeholder for missing data
                    team['missed_shots'], team['hits'], team['giveaways'], team['takeaways'], team['blocked_shots'],
                    0, team['faceoffs_won'], team['faceoffs_lost'], team['powerplays'], 0,  # More placeholders
                   )
            
            cursor.execute('''
                INSERT INTO team_stats_per_game (global_event_id, event_id, global_team_id, team_id, name, global_opponent_id, opponent_id, opponent_name,
                                                  season, date, home_away, result, goals, assists, penalties, penalty_minutes, shots, blocked_att, 
                                                  missed_shots, hits, giveaways, takeaways, blocked_shots, faceoffs, faceoffs_won, faceoffs_lost, 
                                                  powerplays, points)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
        conn.commit()

def main():
    games_to_fetch = get_games_to_fetch(db_path)
    for global_event_id in games_to_fetch:
        fetch_and_insert_team_stats(db_path, global_event_id, api_key)

if __name__ == "__main__":
    main()
