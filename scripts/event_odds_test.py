import sqlite3
from datetime import datetime
import json

# Configuration
db_path = 'assets/data.db'

# Simulated static details for a hypothetical game
static_game_details = {
    'global_event_id': 'simulated_event_id',
    'event_id': 'sr:simulated_event:123456',
    'home_id': 'home_id_simulated',
    'home_team_id': 'sr:team:1234',
    'home_name': 'Simulated Home Team',
    'away_id': 'away_id_simulated',
    'away_team_id': 'sr:team:5678',
    'away_name': 'Simulated Away Team',
    'book_id': 'sr:book:25080'  # Assuming you're always using the consensus book for this example
}

def fetch_event_odds_from_file(file_path):
    """Fetch odds data from a local file for testing."""
    try:
        with open(file_path, 'r') as file:
            odds_data = file.read()
            return json.loads(odds_data)
    except Exception as e:
        print(f"Failed to fetch odds data from file: {e}")
        return None

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
                    'event_id': result[1]
                }
            else:
                print(f"No upcoming games found for team: {name}")
    return games

def parse_odds_data(odds_data):
    """Parse odds data and categorize into winner_odds, spread_odds, and total_odds, home_total_odds, away_total_odds."""
    # Initialize containers for different types of odds
    winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds = {}, {}, {}, {}, {}
    consensus_book_id = "sr:book:25080"

    for market in odds_data.get('markets', []):
        # Assuming 'market' structure is correctly understood
        market_id = market.get('id')
        market_name = market.get('name')
        for book in market.get('books', []):
            if book.get('id') == consensus_book_id:
                if market_name.lower().startswith("winner"):
                    # Extract winner odds
                    outcomes = book.get('outcomes', [])
                    winner_odds['market_id'] = market_id
                    winner_odds['home_winner_odds'] = outcomes[0].get('odds_american')
                    winner_odds['away_winner_odds'] = outcomes[1].get('odds_american')
                elif market_name.lower().startswith("handicap"):
                    # Extract spread odds
                    outcomes = book.get('outcomes', [])
                    spread_odds['market_id'] = market_id
                    spread_odds['home_spread'] = outcomes[0].get('handicap')
                    spread_odds['home_spread_odds'] = outcomes[0].get('odds_american')
                    spread_odds['away_spread'] = outcomes[1].get('handicap')
                    spread_odds['away_spread_odds'] = outcomes[1].get('odds_american')
                elif market_name.lower().startswith("total"):
                    # Extract spread odds
                    outcomes = book.get('outcomes', [])
                    total_odds['market_id'] = market_id
                    total_odds['game_total'] = outcomes[0].get('total')
                    total_odds['game_over_odds'] = outcomes[0].get('odds_american')
                    total_odds['game_under_odds'] = outcomes[1].get('odds_american')   

                elif market_name.lower().startswith("home total"):
                    # Extract spread odds
                    outcomes = book.get('outcomes', [])
                    home_total_odds['market_id'] = market_id
                    home_total_odds['home_total'] = outcomes[0].get('total')
                    home_total_odds['home_over_odds'] = outcomes[0].get('odds_american')
                    home_total_odds['home_under_odds'] = outcomes[1].get('odds_american') 

                elif market_name.lower().startswith("away total"):
                    # Extract spread odds
                    outcomes = book.get('outcomes', [])
                    away_total_odds['market_id'] = market_id
                    away_total_odds['away_total'] = outcomes[0].get('total')
                    away_total_odds['away_over_odds'] = outcomes[0].get('odds_american')
                    away_total_odds['away_under_odds'] = outcomes[1].get('odds_american')  

    return winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds

# Function to insert data into the database
def insert_odds_data(static_details, winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Prepare values for insertion using both static details and parsed odds data
        values_winner = (
            static_details['global_event_id'], static_details['event_id'],
            static_details['home_id'], static_details['home_team_id'], static_details['home_name'],
            static_details['away_id'], static_details['away_team_id'], static_details['away_name'],
            winner_odds.get('market_id'), static_details['book_id'],
            winner_odds.get('home_winner_odds'), winner_odds.get('away_winner_odds')
        )

        values_spread = (
            static_details['global_event_id'], static_details['event_id'],
            static_details['home_id'], static_details['home_team_id'], static_details['home_name'],
            static_details['away_id'], static_details['away_team_id'], static_details['away_name'],
            spread_odds.get('market_id'), static_details['book_id'],
            spread_odds.get('home_spread'), spread_odds.get('home_spread_odds'), spread_odds.get('away_spread'), 
            spread_odds.get('away_spread_odds')
        )

        values_total = (
            static_details['global_event_id'], static_details['event_id'],
            static_details['home_id'], static_details['home_team_id'], static_details['home_name'],
            static_details['away_id'], static_details['away_team_id'], static_details['away_name'],
            total_odds.get('market_id'), static_details['book_id'],
            total_odds.get('game_total'), total_odds.get('game_over_odds'), total_odds.get('game_under_odds')
        )

        values_home_total = (
            static_details['global_event_id'], static_details['event_id'],
            static_details['home_id'], static_details['home_team_id'], static_details['home_name'],
            static_details['away_id'], static_details['away_team_id'], static_details['away_name'],
            home_total_odds.get('market_id'), static_details['book_id'],
            home_total_odds.get('home_total'), home_total_odds.get('home_over_odds'), home_total_odds.get('home_under_odds')
        )

        values_away_total = (
            static_details['global_event_id'], static_details['event_id'],
            static_details['home_id'], static_details['home_team_id'], static_details['home_name'],
            static_details['away_id'], static_details['away_team_id'], static_details['away_name'],
            away_total_odds.get('market_id'), static_details['book_id'],
            away_total_odds.get('away_total'), away_total_odds.get('away_over_odds'), away_total_odds.get('away_under_odds')
        )
        
        # Insertion for winner_odds - Repeat similar steps for spread_odds and total_odds
        insert_query_winner = '''
        INSERT INTO winner_odds (
            global_event_id, event_id, home_id, home_team_id, home_name,
            away_id, away_team_id, away_name, market_id, book_id,
            home_winner_odds, away_winner_odds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_query_winner, values_winner)
        
        # Insertion for winner_odds - Repeat similar steps for spread_odds and total_odds
        insert_query_spread = '''
        INSERT INTO spread_odds (
            global_event_id, event_id, home_id, home_team_id, home_name,
            away_id, away_team_id, away_name, market_id, book_id, home_spread,
            home_spread_odds, away_spread, away_spread_odds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_query_spread, values_spread)

        # Insertion for winner_odds - Repeat similar steps for spread_odds and total_odds
        insert_query_total = '''
        INSERT INTO total_odds (
            global_event_id, event_id, home_id, home_team_id, home_name,
            away_id, away_team_id, away_name, market_id, book_id,
            game_total, game_over_odds, game_under_odds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_query_total, values_total)

        insert_query_home_total = '''
        INSERT INTO home_total_odds (
            global_event_id, event_id, home_id, home_team_id, home_name,
            away_id, away_team_id, away_name, market_id, book_id,
            home_total, home_over_odds, home_under_odds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_query_home_total, values_home_total)

        insert_query_away_total = '''
        INSERT INTO away_total_odds (
            global_event_id, event_id, home_id, home_team_id, home_name,
            away_id, away_team_id, away_name, market_id, book_id,
            away_total, away_over_odds, away_under_odds
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(insert_query_away_total, values_away_total)

        conn.commit()

# Fetch and parse the odds data from the file
odds_data = fetch_event_odds_from_file('api_response.txt')  # Ensure this points to the correct path
winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds = parse_odds_data(odds_data)

# Call the function to insert the data
insert_odds_data(static_game_details, winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds)