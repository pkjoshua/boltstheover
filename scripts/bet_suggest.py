import sqlite3
from datetime import datetime

# Configuration
db_path = 'assets/data.db'

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
    """Find the next game for each team and indicate if they're home or away."""
    games = {}
    # Get today's date without time for comparison
    today_date = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        for name, team_id in team_ids.items():
            c.execute("""
                SELECT global_event_id, event_id, date, home_team_id, away_team_id
                FROM schedule
                WHERE date(date) >= date(?) AND (home_team_id = ? OR away_team_id = ?)
                ORDER BY date ASC
                LIMIT 1
            """, (today_date, team_id, team_id))
            result = c.fetchone()
            if result:
                home_or_away = "home" if result[3] == team_id else "away"
                games[name] = {
                    'global_event_id': result[0],
                    'event_id': result[1],
                    'date': result[2],
                    'home_team_id': result[3],
                    'away_team_id': result[4],
                    'home_or_away': home_or_away
                }
            else:
                print(f"No upcoming games found for team: {name}")
    return games


def fetch_team_stats(team_id, home_or_away):
    """Fetch team statistics for calculating KPIs."""
    stats = {}
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = """
            SELECT AVG(goals), AVG(shots), AVG(powerplays), AVG(penalty_minutes)
            FROM team_stats_per_game
            WHERE team_id = ? AND home_away = ?
        """
        c.execute(query, (team_id, home_or_away))
        result = c.fetchone()
        if result:
            stats = {
                'avg_goals': result[0],
                'avg_shots': result[1],
                'avg_powerplays': result[2],
                'avg_penalty_minutes': result[3]
            }
        return stats

def fetch_opposing_team_stats(opposing_team_id, home_or_away):
    """Fetch team statistics for calculating KPIs."""
    stats = {}
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = """
            SELECT AVG(goals), AVG(shots), AVG(powerplays), AVG(penalty_minutes)
            FROM team_stats_per_game
            WHERE team_id = ? AND home_away = ?
        """
        c.execute(query, (opposing_team_id, home_or_away))
        result = c.fetchone()
        if result:
            stats = {
                'avg_goals': result[0],
                'avg_shots': result[1],
                'avg_powerplays': result[2],
                'avg_penalty_minutes': result[3]
            }
        return stats

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

def fetch_head_to_head_stats(team_id, opposing_team_id):
    """Fetch combined head-to-head statistics for the two teams."""
    head_to_head_stats = {}
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # Adjust the query to fetch and sum/average the stats for both teams
        query = """
            SELECT 
                SUM(goals) AS total_goals, 
                AVG(shots) AS avg_shots, 
                SUM(penalty_minutes) AS total_penalty_minutes
            FROM (
                SELECT 
                    goals, 
                    shots, 
                    penalty_minutes 
                FROM team_stats_per_game
                WHERE (team_id = ? AND opponent_id = ?)
                UNION ALL
                SELECT 
                    goals, 
                    shots, 
                    penalty_minutes 
                FROM team_stats_per_game
                WHERE (team_id = ? AND opponent_id = ?)
            )
        """
        c.execute(query, (team_id, opposing_team_id, opposing_team_id, team_id))
        result = c.fetchone()
        if result:
            head_to_head_stats = {
                'total_goals': result[0],
                'avg_shots': result[1],
                'total_penalty_minutes': result[2]
            }
        return head_to_head_stats

def fetch_individual_game_stats(team_id, opposing_team_id):
    """Fetch goals and shots for each game between the two teams, ensuring no duplicates."""
    game_stats = []
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = """
            SELECT a.event_id, a.goals AS team_goals, a.shots AS team_shots, b.goals AS opp_goals, b.shots AS opp_shots
            FROM team_stats_per_game AS a
            JOIN team_stats_per_game AS b ON a.event_id = b.event_id AND a.team_id != b.team_id
            WHERE a.team_id = ? AND b.team_id = ?
            ORDER BY a.event_id
        """
        c.execute(query, (team_id, opposing_team_id))
        results = c.fetchall()
        for result in results:
            game_stats.append({
                'event_id': result[0],
                'team_goals': result[1],
                'team_shots': result[2],
                'opp_goals': result[3],
                'opp_shots': result[4],
            })
    return game_stats

def fetch_last_10_games_stats(team_id):
    """Fetch statistics for the last 10 games played by the team."""
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        query = """
            SELECT AVG(goals), AVG(shots), AVG(powerplays), AVG(penalty_minutes)
            FROM team_stats_per_game
            WHERE team_id = ?
            ORDER BY event_id DESC
            LIMIT 10
        """
        c.execute(query, (team_id,))
        result = c.fetchone()
        if result:
            return {
                'avg_goals': result[0],
                'avg_shots': result[1],
                'avg_powerplays': result[2],
                'avg_penalty_minutes': result[3]
            }
        else:
            return {'avg_goals': 0, 'avg_shots': 0, 'avg_powerplays': 0, 'avg_penalty_minutes': 0}

def fetch_game_odds(event_id):
    """Fetch odds information for a specific game across all odds tables."""
    odds_info = {}
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        
        # Fetch winner odds
        c.execute("""
            SELECT home_winner_odds, away_winner_odds
            FROM winner_odds
            WHERE event_id = ?
        """, (event_id,))
        winner_odds = c.fetchone()
        if winner_odds:
            odds_info['winner_odds'] = {'home_winner_odds': winner_odds[0], 'away_winner_odds': winner_odds[1]}
        
        # Fetch spread odds
        c.execute("""
            SELECT home_spread, home_spread_odds, away_spread, away_spread_odds
            FROM spread_odds
            WHERE event_id = ?
        """, (event_id,))
        spread_odds = c.fetchone()
        if spread_odds:
            odds_info['spread_odds'] = {
                'home_spread': spread_odds[0], 'home_spread_odds': spread_odds[1],
                'away_spread': spread_odds[2], 'away_spread_odds': spread_odds[3]
            }
        
        # Fetch total odds
        c.execute("""
            SELECT game_total, game_over_odds, game_under_odds
            FROM total_odds
            WHERE event_id = ?
        """, (event_id,))
        total_odds = c.fetchone()
        if total_odds:
            odds_info['total_odds'] = {
                'game_total': total_odds[0], 'game_over_odds': total_odds[1], 'game_under_odds': total_odds[2]
            }
        
        # Fetch home total odds
        c.execute("""
            SELECT home_total, home_over_odds, home_under_odds
            FROM home_total_odds
            WHERE event_id = ?
        """, (event_id,))
        home_total_odds = c.fetchone()
        if home_total_odds:
            odds_info['home_total_odds'] = {
                'home_total': home_total_odds[0], 'home_over_odds': home_total_odds[1], 'home_under_odds': home_total_odds[2]
            }
        
        # Fetch away total odds
        c.execute("""
            SELECT away_total, away_over_odds, away_under_odds
            FROM away_total_odds
            WHERE event_id = ?
        """, (event_id,))
        away_total_odds = c.fetchone()
        if away_total_odds:
            odds_info['away_total_odds'] = {
                'away_total': away_total_odds[0], 'away_over_odds': away_total_odds[1], 'away_under_odds': away_total_odds[2]
            }
        
    return odds_info

def suggest_bets(team_name, opposing_team_name, team_stats, opposing_team_stats, head_to_head_stats, odds_info):
    # Simplified version for demonstration. Adjust logic as needed.
    suggestions = []
    # Example logic for winner bet suggestion
    if float(odds_info.get('winner_odds', {}).get('home_winner_odds', 0)) < float(odds_info.get('winner_odds', {}).get('away_winner_odds', 0)):
        suggestions.append(f"Consider betting on {team_name} to win.")
    else:
        suggestions.append(f"Consider betting on {opposing_team_name} to win.")
    
    # Example logic for over/under bet suggestion
    total_goals_predicted = (team_stats['avg_goals'] + opposing_team_stats['avg_goals']) / 2
    if total_goals_predicted > float(odds_info.get('total_odds', {}).get('game_total', 0)):
        suggestions.append("Consider betting on the Over.")
    else:
        suggestions.append("Consider betting on the Under.")
    
    return suggestions

def print_and_write(line, file):
    print(line)
    file.write(line + "\n")

def main():
    # Open a file for writing
    with open('betting_stats.txt', 'w') as stats_file:
        team_names = get_latest_team_name_from_file()
        team_ids = get_team_ids([team_names])

        print_and_write("Team IDs:", stats_file)
        for team_name, team_id in team_ids.items():
            print_and_write(f"- {team_name}: {team_id}", stats_file)

        next_games = find_next_game(team_ids)

        print_and_write("\nNext Game:", stats_file)
        for team_name, game_details in next_games.items():
            # Your existing logic to process each game and stats
            # Determine the opposing team's ID
            opposing_team_id = game_details['away_team_id'] if game_details['home_team_id'] == team_ids[team_name] else game_details['home_team_id']

            # Fetch the opponent's name using the opposing team's ID
            opposing_team_name = get_opponent_name(opposing_team_id)

            team_stats = fetch_team_stats(team_ids[team_name], game_details['home_or_away'])
            opposing_team_stats = fetch_team_stats(opposing_team_id, game_details['home_or_away'])

            head_to_head_stats = fetch_head_to_head_stats(team_ids[team_name], opposing_team_id)

            # Fetch the last 10 games stats for both teams
            team_last_10_games_stats = fetch_last_10_games_stats(team_ids[team_name])
            opposing_team_last_10_games_stats = fetch_last_10_games_stats(opposing_team_id)

            # Fetch individual game stats for both teams
            individual_game_stats = fetch_individual_game_stats(team_ids[team_name], opposing_team_id)

            # Fetch odds information for the event_id
            event_id = game_details['event_id']
            odds_info = fetch_game_odds(event_id)

            bet_suggestions = suggest_bets(team_name, opposing_team_name, team_stats, opposing_team_stats, head_to_head_stats, odds_info)
            # Example of using print_and_write for one of the lines
            print_and_write(f"- {team_name}'s next game is {game_details['home_or_away']} against the {opposing_team_name} (Team ID: {opposing_team_id})", stats_file)
            # Game details
            print_and_write(f"  Global Event ID: {game_details['global_event_id']}", stats_file)
            print_and_write(f"  Event ID: {game_details['event_id']}", stats_file)
            print_and_write(f"  Date: {game_details['date']}", stats_file)
            print_and_write(f"  Home Team ID: {game_details['home_team_id']}", stats_file)
            print_and_write(f"  Away Team ID: {game_details['away_team_id']}", stats_file)
            # Team season KPIs
            print_and_write(f"\n -- {team_name} KPIs --", stats_file)
            print_and_write(f"  Average Goals: {team_stats['avg_goals']}", stats_file)
            print_and_write(f"  Average Shots: {team_stats['avg_shots']}", stats_file)
            print_and_write(f"  Average Powerplays: {team_stats['avg_powerplays']}", stats_file)
            print_and_write(f"  Average Penalty Minutes: {team_stats['avg_penalty_minutes']}", stats_file)
            # Opponent season KPIs
            print_and_write(f"\n -- {opposing_team_name} KPIs --", stats_file)
            print_and_write(f"  Average Goals: {opposing_team_stats['avg_goals']}", stats_file)
            print_and_write(f"  Average Shots: {opposing_team_stats['avg_shots']}", stats_file)
            print_and_write(f"  Average Powerplays: {opposing_team_stats['avg_powerplays']}", stats_file)
            print_and_write(f"  Average Penalty Minutes: {opposing_team_stats['avg_penalty_minutes']}", stats_file)
            # H2H KPIs
            print_and_write(f"\n -- H2H KPIs --", stats_file)
            print_and_write(f"  Head-to-Head Stats {team_name} vs {get_opponent_name(opposing_team_id)}:", stats_file)
            print_and_write(f"  Total Goals: {head_to_head_stats['total_goals']}", stats_file)
            print_and_write(f"  Average Shots: {head_to_head_stats['avg_shots']}", stats_file)

            # Print individual game stats for both teams
            print_and_write(f"\n -- Individual Game Stats: {team_name} vs {opposing_team_name} --", stats_file)
            for game_stat in individual_game_stats:
                print_and_write(f"  Game ID: {game_stat['event_id']}, "
                    f"{team_name} Goals: {game_stat['team_goals']}, Shots: {game_stat['team_shots']}; "
                    f"{opposing_team_name} Goals: {game_stat['opp_goals']}, Shots: {game_stat['opp_shots']}", stats_file)

            print_and_write(f"\n -- {team_name} Last 10 Games Stats --", stats_file)
            print_and_write(f"  Average Goals: {team_last_10_games_stats['avg_goals']}", stats_file)
            print_and_write(f"  Average Shots: {team_last_10_games_stats['avg_shots']}", stats_file)
            print_and_write(f"  Average Powerplays: {team_last_10_games_stats['avg_powerplays']}", stats_file)
            print_and_write(f"  Average Penalty Minutes: {team_last_10_games_stats['avg_penalty_minutes']}", stats_file)

            print_and_write(f"\n -- {opposing_team_name} Last 10 Games Stats --", stats_file)
            print_and_write(f"  Average Goals: {opposing_team_last_10_games_stats['avg_goals']}", stats_file)
            print_and_write(f"  Average Shots: {opposing_team_last_10_games_stats['avg_shots']}", stats_file)
            print_and_write(f"  Average Powerplays: {opposing_team_last_10_games_stats['avg_powerplays']}", stats_file)
            print_and_write(f"  Average Penalty Minutes: {opposing_team_last_10_games_stats['avg_penalty_minutes']}", stats_file)

            # Display the odds information
            print_and_write("\nOdds Information:", stats_file)
            for odds_type, odds_values in odds_info.items():
                print_and_write(f"- {odds_type}:", stats_file)
                for key, value in odds_values.items():
                    print_and_write(f"  {key}: {value}", stats_file)            # Continue with the rest of your stats printing using print_and_write

            # Example for bet suggestions
            print_and_write("\nBet Suggestions:", stats_file)
            for suggestion in bet_suggestions:
                print_and_write(f"- {suggestion}", stats_file)

if __name__ == "__main__":
    main()
