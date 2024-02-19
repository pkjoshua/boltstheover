from datetime import datetime
import sqlite3

# Configuration
db_path = 'assets/data.db'

def fetch_previous_games(team_id):
    """Fetch the last 15 games for a given team before today's date, ignoring the time."""
    # Format today's date to include the end of the day for comparison
    today_date = datetime.now().strftime('%Y-%m-%d 23:59:59')
    
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = """
        SELECT global_event_id
        FROM schedule
        WHERE (home_team_id = ? OR away_team_id = ?) AND strftime('%Y-%m-%d %H:%M:%S', date) < ?
        ORDER BY strftime('%Y-%m-%d %H:%M:%S', date) DESC
        LIMIT 15
        """
        c.execute(query, (team_id, team_id, today_date))
        games = c.fetchall()
        return [game[0] for game in games]

# Example usage
team_id = 3687  # Example team_id for Panthers
games = fetch_previous_games(team_id)
print("Fetched games:", games)
