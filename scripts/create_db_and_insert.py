import sqlite3
import os

# Define the path to the SQLite database
db_path = os.path.join('assets', 'data.db')

# Check if the database file already exists
if os.path.exists(db_path):
    print("Database already exists.")

# Connect to the SQLite database (this will create it if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# roster schema (unchanged)
cursor.execute('''
CREATE TABLE IF NOT EXISTS roster (
    team_id TEXT,
    player_id TEXT PRIMARY KEY,
    name TEXT,
    jersey_number TEXT,
    age TEXT,
    height TEXT,
    weight TEXT,
    shot TEXT,
    position TEXT
)
''')

# Updated player_stats schema to match provided stats
cursor.execute('''
CREATE TABLE IF NOT EXISTS player_stats (
    team_id TEXT,
    player_id TEXT,
    game_id TEXT,
    date TEXT,
    opponent TEXT,
    result TEXT,
    score TEXT,
    goals TEXT,
    assists TEXT,
    points TEXT,
    plus_minus TEXT,
    penalty_minutes TEXT,
    shots TEXT,
    shot_percentage TEXT,
    pp_goals TEXT,
    pp_assists TEXT,
    sh_goals TEXT,
    sh_assists TEXT,
    gw_goals TEXT,
    toi TEXT,
    pt TEXT,
    PRIMARY KEY (player_id, game_id)
)
''')

# schedule schema (unchanged)
cursor.execute('''
CREATE TABLE IF NOT EXISTS schedules (
    team_id TEXT,
    gameid TEXT PRIMARY KEY,
    date TEXT,
    home_away TEXT,
    opponent TEXT,
    win_loss TEXT,
    result_score TEXT,
    record TEXT,
    goalie TEXT,
    top_performer TEXT
)
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

def insert_player_stats_data(player_stats):
    """Insert or update player stats data into the SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for stats in player_stats:
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO player_stats (team_id, player_id, game_id, date, opponent, result, score, goals, assists, points, plus_minus, penalty_minutes, shots, shot_percentage, pp_goals, pp_assists, sh_goals, sh_assists, gw_goals, toi, pt)
            VALUES (:team_id, :player_id, :game_id, :date, :opponent, :result, :score, :goals, :assists, :points, :plus_minus, :penalty_minutes, :shots, :shot_percentage, :pp_goals, :pp_assists, :sh_goals, :sh_assists, :gw_goals, :toi, :pt)
            ''', stats)
        except sqlite3.IntegrityError as e:
            print(f"Error inserting data: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    
    conn.commit()
    conn.close()
