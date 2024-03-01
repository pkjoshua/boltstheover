import sqlite3
import os

# Database path
db_path = 'assets/data.db'

# Ensure the assets directory exists
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# Connect to the SQLite database (it will be created if it doesn't exist)
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create the 'teams' table
c.execute('''
CREATE TABLE IF NOT EXISTS teams (
    league_id TEXT,
    conference_id TEXT,
    conference_name TEXT,
    division_id TEXT,
    division_name TEXT,
    global_team_id TEXT,
    team_id TEXT PRIMARY KEY,
    name TEXT,
    alias TEXT
)
''')

# Create the 'schedule' table
c.execute('''
CREATE TABLE IF NOT EXISTS schedule (
    season_id TEXT,
    season INTEGER,
    global_event_id TEXT,
    status TEXT,
    date TEXT,
    home_points INTEGER,
    away_points INTEGER,
    event_id TEXT,
    home_id TEXT,
    home_name TEXT,
    home_alias TEXT,
    home_team_id TEXT,
    away_id TEXT,
    away_name TEXT,
    away_alias TEXT,
    away_team_id TEXT,
    winner_team_id TEXT,
    winner_name TEXT,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    UNIQUE(global_event_id)
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS team_stats_per_game (
    global_event_id TEXT,
    event_id TEXT,
    global_team_id TEXT,
    team_id TEXT,
    name TEXT,
    global_opponent_id TEXT,
    opponent_id TEXT,
    opponent_name TEXT,
    season TEXT,
    date TEXT,
    home_away TEXT,
    result TEXT,
    goals INTEGER,
    assists INTEGER,
    penalties INTEGER,
    penalty_minutes INTEGER,
    shots INTEGER,
    blocked_att INTEGER,
    missed_shots INTEGER,
    hits INTEGER,
    giveaways INTEGER,
    takeaways INTEGER,
    blocked_shots INTEGER,
    faceoffs_won INTEGER,
    faceoffs_lost INTEGER,
    powerplays INTEGER,
    points INTEGER,
    PRIMARY KEY (global_event_id, global_team_id)
)
''')

# Create the 'winner_odds' table
c.execute('''
CREATE TABLE IF NOT EXISTS winner_odds (
    global_event_id TEXT,
    event_id TEXT,
    home_id TEXT,
    home_team_id TEXT,
    home_name TEXT,
    away_id TEXT,
    away_team_id TEXT,
    away_name TEXT,
    market_id TEXT,
    book_id TEXT,
    home_winner_odds TEXT,
    away_winner_odds TEXT,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    UNIQUE(global_event_id, event_id, book_id)
)
''')

# Create the 'spread' table
c.execute('''
CREATE TABLE IF NOT EXISTS spread_odds (
    global_event_id TEXT,
    event_id TEXT,
    home_id TEXT,
    home_team_id TEXT,
    home_name TEXT,
    away_id TEXT,
    away_team_id TEXT,
    away_name TEXT,
    market_id TEXT,
    book_id TEXT,
    home_spread TEXT,
    home_spread_odds TEXT,
    away_spread TEXT,
    away_spread_odds TEXT,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    UNIQUE(global_event_id, event_id, book_id)
)
''')

# Create the 'total_odds' table
c.execute('''
CREATE TABLE IF NOT EXISTS total_odds (
    global_event_id TEXT,
    event_id TEXT,
    home_id TEXT,
    home_team_id TEXT,
    home_name TEXT,
    away_id TEXT,
    away_team_id TEXT,
    away_name TEXT,
    market_id TEXT,
    book_id TEXT,
    game_total,
    game_over_odds TEXT,
    game_under_odds TEXT,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    UNIQUE(global_event_id, event_id, book_id)
)
''')

# Create the 'total_odds' table
c.execute('''
CREATE TABLE IF NOT EXISTS home_total_odds (
    global_event_id TEXT,
    event_id TEXT,
    home_id TEXT,
    home_team_id TEXT,
    home_name TEXT,
    away_id TEXT,
    away_team_id TEXT,
    away_name TEXT,
    market_id TEXT,
    book_id TEXT,
    home_total TEXT,
    home_over_odds TEXT,
    home_under_odds TEXT,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    UNIQUE(global_event_id, event_id, book_id)
)
''')

# Create the 'total_odds' table
c.execute('''
CREATE TABLE IF NOT EXISTS away_total_odds (
    global_event_id TEXT,
    event_id TEXT,
    home_id TEXT,
    home_team_id TEXT,
    home_name TEXT,
    away_id TEXT,
    away_team_id TEXT,
    away_name TEXT,
    market_id TEXT,
    book_id TEXT,
    away_total TEXT,
    away_over_odds TEXT,
    away_under_odds TEXT,
    FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
    FOREIGN KEY (away_team_id) REFERENCES teams(team_id),
    UNIQUE(global_event_id, event_id, book_id)
)
''')

# Commit the changes and close the database connection
conn.commit()
conn.close()

print("Database and tables have been successfully created.")
