import sqlite3
from datetime import datetime

# Configuration
db_path = 'assets/data.db'

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
                SELECT global_event_id, event_id, date, home_team_id, away_team_id
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
                    'date': result[2],
                    'home_team_id': result[3],
                    'away_team_id': result[4]
                }
            else:
                print(f"No upcoming games found for team: {name}")
    return games

def get_opponent_name(opponent_team_id):
    """Fetch opponent name for given team_id."""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = "SELECT name FROM teams WHERE team_id = ?"
        c.execute(query, (opponent_team_id,))
        result = c.fetchone()
        if result:
            return result[0]
        else:
            return "Unknown Opponent"


# Output to terminal
team_names = ["Lightning"]
team_ids = get_team_ids(team_names)

print("Team IDs:")
for team_name, team_id in team_ids.items():
    print(f"- {team_name}: {team_id}")

next_games = find_next_game(team_ids)

print("\nNext Games:")
for team_name, game_details in next_games.items():
    print(f"- {team_name}'s next game:")
    print(f"  Global Event ID: {game_details['global_event_id']}")
    print(f"  Event ID: {game_details['event_id']}")
    print(f"  Date: {game_details['date']}")
    print(f"  Home Team ID: {game_details['home_team_id']}")
    print(f"  Away Team ID: {game_details['away_team_id']}")

    # Determine the opposing team's ID
    opposing_team_id = game_details['away_team_id'] if game_details['home_team_id'] == team_ids[team_name] else game_details['home_team_id']

    # Fetch the opponent's name using the opposing team's ID
    opposing_team_name = get_opponent_name(opposing_team_id)

    print(f"  Opponent Team: {opposing_team_name} (Team ID: {opposing_team_id})\n")


