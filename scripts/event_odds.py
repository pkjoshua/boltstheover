import requests
import sqlite3
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
db_path = 'assets/data.db'
api_key = 'j7k2wp4a2my3qj9sqhq8fkr5'  # Replace with your actual API key

# Book ID we are searching for 
book_id = "sr:book:25080"

def get_latest_team_name_from_file():
    with open('team_name.txt', 'r') as f:
        team_name = f.read().strip()
    return team_name

def fetch_event_odds(event_id, api_key):
    """Fetch odds data for a given event_id."""
    url = f"https://api.sportradar.us/oddscomparison-prematch/trial/v2/en/sport_events/sr:sport_event:{event_id}/sport_event_markets.json?api_key={api_key}"
    response = requests.get(url)
    time.sleep(5)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch odds data for event {event_id}: HTTP {response.status_code}")
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

def parse_odds_data(odds_data):
    """Parse odds data and categorize into winner_odds, spread_odds, and total_odds, home_total_odds, away_total_odds."""
    # Initialize containers for different types of odds
    winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds = {}, {}, {}, {}, {}

    for market in odds_data.get('markets', []):
        # Assuming 'market' structure is correctly understood
        market_id = market.get('id')
        market_name = market.get('name')
        for book in market.get('books', []):
            if book.get('id') == book_id:
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
def insert_odds_data(game_details, winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        for team_name, game_details in games.items():
            print(f"Processing and inserting odds data for {team_name}'s next game (Event ID: {game_details['event_id']})...")
            # Fetch and parse the odds data
            odds_data = fetch_event_odds(game_details['event_id'], api_key)
            if odds_data:
                winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds = parse_odds_data(odds_data)
        
                # Prepare values for insertion using both static details and parsed odds data
                values_winner = (
                    game_details['global_event_id'], game_details['event_id'],
                    game_details['home_id'], game_details['home_team_id'], game_details['home_name'],
                    game_details['away_id'], game_details['away_team_id'], game_details['away_name'],
                    winner_odds.get('market_id'), book_id,
                    winner_odds.get('home_winner_odds'), winner_odds.get('away_winner_odds')
                )

                values_spread = (
                    game_details['global_event_id'], game_details['event_id'],
                    game_details['home_id'], game_details['home_team_id'], game_details['home_name'],
                    game_details['away_id'], game_details['away_team_id'], game_details['away_name'],
                    spread_odds.get('market_id'), book_id,
                    spread_odds.get('home_spread'), spread_odds.get('home_spread_odds'), spread_odds.get('away_spread'), 
                    spread_odds.get('away_spread_odds')
                )

                values_total = (
                    game_details['global_event_id'], game_details['event_id'],
                    game_details['home_id'], game_details['home_team_id'], game_details['home_name'],
                    game_details['away_id'], game_details['away_team_id'], game_details['away_name'],
                    total_odds.get('market_id'), book_id,
                    total_odds.get('game_total'), total_odds.get('game_over_odds'), total_odds.get('game_under_odds')
                )

                values_home_total = (
                    game_details['global_event_id'], game_details['event_id'],
                    game_details['home_id'], game_details['home_team_id'], game_details['home_name'],
                    game_details['away_id'], game_details['away_team_id'], game_details['away_name'],
                    home_total_odds.get('market_id'), book_id,
                    home_total_odds.get('home_total'), home_total_odds.get('home_over_odds'), home_total_odds.get('home_under_odds')
                )

                values_away_total = (
                    game_details['global_event_id'], game_details['event_id'],
                    game_details['home_id'], game_details['home_team_id'], game_details['home_name'],
                    game_details['away_id'], game_details['away_team_id'], game_details['away_name'],
                    away_total_odds.get('market_id'), book_id,
                    away_total_odds.get('away_total'), away_total_odds.get('away_over_odds'), away_total_odds.get('away_under_odds')
                )

                # Insertion for winner_odds - Repeat similar steps for spread_odds and total_odds
                insert_query_winner = '''
                INSERT OR REPLACE INTO winner_odds (
                    global_event_id, event_id, home_id, home_team_id, home_name,
                    away_id, away_team_id, away_name, market_id, book_id,
                    home_winner_odds, away_winner_odds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor.execute(insert_query_winner, values_winner)
                
                # Insertion for winner_odds - Repeat similar steps for spread_odds and total_odds
                insert_query_spread = '''
                INSERT OR REPLACE INTO spread_odds (
                    global_event_id, event_id, home_id, home_team_id, home_name,
                    away_id, away_team_id, away_name, market_id, book_id, home_spread,
                    home_spread_odds, away_spread, away_spread_odds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor.execute(insert_query_spread, values_spread)

                # Insertion for winner_odds - Repeat similar steps for spread_odds and total_odds
                insert_query_total = '''
                INSERT OR REPLACE INTO total_odds (
                    global_event_id, event_id, home_id, home_team_id, home_name,
                    away_id, away_team_id, away_name, market_id, book_id,
                    game_total, game_over_odds, game_under_odds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor.execute(insert_query_total, values_total)

                insert_query_home_total = '''
                INSERT OR REPLACE INTO home_total_odds (
                    global_event_id, event_id, home_id, home_team_id, home_name,
                    away_id, away_team_id, away_name, market_id, book_id,
                    home_total, home_over_odds, home_under_odds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor.execute(insert_query_home_total, values_home_total)

                insert_query_away_total = '''
                INSERT OR REPLACE INTO away_total_odds (
                    global_event_id, event_id, home_id, home_team_id, home_name,
                    away_id, away_team_id, away_name, market_id, book_id,
                    away_total, away_over_odds, away_under_odds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
                cursor.execute(insert_query_away_total, values_away_total)

                conn.commit()

team_names = get_latest_team_name_from_file()
team_ids = get_team_ids([team_names])

games = find_next_game(team_ids)

# For each game, fetch event odds from the API and parse the data
for team_name, game_details in games.items():
    print(f"Fetching odds for {team_name}'s next game (Event ID: {game_details['event_id']})...")
    odds_data = fetch_event_odds(game_details['event_id'], api_key)
    if odds_data:
        winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds = parse_odds_data(odds_data)
        insert_odds_data(game_details, winner_odds, spread_odds, total_odds, home_total_odds, away_total_odds)
        logging.info("Stats inserted")
    else:
        print("Failed to fetch or parse odds data.")
        logging.info("Fetching odds failed")

