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
                opponent_team_id = result[4] if result[3] == team_id else result[3]
                opponent_name = get_opponent_name(opponent_team_id)
                games[name] = {
                    'global_event_id': result[0],
                    'event_id': result[1],
                    'date': result[2],
                    'home_team_id': result[3],
                    'away_team_id': result[4],
                    'opponent_name': opponent_name,
                    'opponent_team_id': opponent_team_id
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

def fetch_team_stats(team_id, games_limit=15):
    """Fetch the last N games' stats for a team."""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT * FROM team_stats_per_game
            WHERE team_id = ?
            ORDER BY date DESC
            LIMIT ?
        """, (team_id, games_limit))
        return c.fetchall()

def calculate_kpis(stats):
    """Calculate KPIs based on team stats."""
    games_played = len(stats)
    if games_played == 0:
        return None  # Handle case with no games

    wins = sum(1 for game in stats if game[11] == 'W')  # 'result' column index
    goals_for = sum(game[12] for game in stats)  # 'goals' column index
    powerplays = sum(game[25] for game in stats)  # 'powerplays' column index
    powerplay_goals = sum(game[12] for game in stats if game[25] > 0)  # Simplified, adjust as needed
    faceoffs_won = sum(game[23] for game in stats)  # 'faceoffs_won' column index
    faceoffs_total = sum(game[23] + game[24] for game in stats)  # 'faceoffs_won' + 'faceoffs_lost'
    shots = sum(game[16] for game in stats)  # 'shots' column index

    kpis = {
        'Winning Percentage': wins / games_played * 100,
        'Goals For Average': goals_for / games_played,
        'Power Play Percentage': powerplay_goals / powerplays * 100 if powerplays > 0 else 0,
        'Shots on Goal Average': shots / games_played,
        'Faceoff Win Percentage': faceoffs_won / faceoffs_total * 100 if faceoffs_total > 0 else 0,
        # Add other KPIs here
    }
    return kpis

def fetch_head_to_head_performance(team_id, opponent_id):
    """Fetch head-to-head win rate against a specific opponent."""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT result FROM team_stats_per_game
            WHERE team_id = ? AND opponent_id = ?
        """, (team_id, opponent_id))
        results = c.fetchall()
        wins = sum(1 for result in results if result[0] == 'W')
        total_games = len(results)
        win_rate = wins / total_games * 100 if total_games > 0 else 0
        return win_rate

# Main logic
team_names = ["Lightning"]
team_ids = get_team_ids(team_names)
next_games = find_next_game(team_ids)

for team_name, game_details in next_games.items():
    print(f"\nAnalyzing {team_name}'s upcoming game against {game_details['opponent_name']}:")
    
    # Determine if the queried team is playing at home or away
    home_or_away = "Home" if team_ids[team_name] == game_details['home_team_id'] else "Away"
    
    # Fetch team stats for both home and away teams
    team_stats = fetch_team_stats(team_ids[team_name])
    opponent_stats = fetch_team_stats(game_details['opponent_team_id'])
    
    # Calculate KPIs for both teams
    team_kpis = calculate_kpis(team_stats)
    opponent_kpis = calculate_kpis(opponent_stats)
    
    # Display KPIs for the queried team
    print(f"{home_or_away} Team ({team_name}) KPIs:")
    for kpi, value in team_kpis.items():
        print(f"{kpi}: {value:.2f}")
    
    # Display KPIs for the opponent
    print(f"Opponent Team ({game_details['opponent_name']}) KPIs:")
    for kpi, value in opponent_kpis.items():
        print(f"{kpi}: {value:.2f}")
    
    # Fetch and display head-to-head performance
    h2h_performance = fetch_head_to_head_performance(team_ids[team_name], game_details['opponent_team_id'])
    print(f"Head-to-Head Win Rate ({team_name} vs. {game_details['opponent_name']}): {h2h_performance:.2f}%")