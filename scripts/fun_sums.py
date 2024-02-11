import sqlite3
import os

db_path = os.path.join('assets', 'data.db')
summary_file_path = os.path.join('assets', 'summary.txt')

def calculate_summary():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Count unique player IDs
    cursor.execute('SELECT COUNT(DISTINCT player_id) FROM roster')
    unique_players = cursor.fetchone()[0]

    # Calculate average age of players
    cursor.execute('SELECT AVG(age) FROM roster')
    avg_age = cursor.fetchone()[0]

    # Most common shooting hand
    cursor.execute('SELECT shot, COUNT(shot) AS count FROM roster GROUP BY shot ORDER BY count DESC LIMIT 1')
    common_shot = cursor.fetchone()

    # Count of games played (excluding NULL results)
    cursor.execute("SELECT COUNT(*) FROM schedules WHERE win_loss IS NOT NULL")
    games_played = cursor.fetchone()[0]

    # Tampa Bay Lightning specific insights
    # Count of Tampa Bay Lightning players
    cursor.execute("SELECT COUNT(*) FROM roster WHERE team_id = '20'")
    tb_players = cursor.fetchone()[0]

    # Average points of Tampa Bay Lightning players
    cursor.execute("""
    SELECT AVG(points) FROM player_stats
    JOIN roster ON player_stats.player_id = roster.player_id
    WHERE roster.team_id = '20'
    """)
    avg_points_tb = cursor.fetchone()[0]

    # Writing summary to a file
    with open(summary_file_path, 'w') as f:
        f.write(f"Unique Player IDs: {unique_players}\n")
        f.write(f"Average Age of Players: {avg_age:.2f}\n")
        f.write(f"Most Common Shooting Hand: {common_shot[0]} ({common_shot[1]} players)\n")
        f.write(f"Games Played: {games_played}\n")
        f.write(f"Tampa Bay Lightning Players: {tb_players}\n")
        f.write(f"Average Points of Tampa Bay Lightning Players: {avg_points_tb:.2f}\n")

    conn.close()

calculate_summary()
