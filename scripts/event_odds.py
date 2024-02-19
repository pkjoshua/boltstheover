import requests
import sqlite3
from datetime import datetime

def fetch_event_odds(event_id, api_key):
    """Fetch odds data for a given event_id."""
    url = f"https://api.sportradar.us/oddscomparison-prematch/trial/v2/en/sport_events/sr:sport_event:{event_id}/sport_event_markets.json?api_key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch odds data for event {event_id}: HTTP {response.status_code}")
        return None

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

def parse_odds_data(odds_data):
    """Parse odds data and categorize into winner_odds, spread_odds, and total_odds."""
    # Initialize containers for different types of odds
    winner_odds, spread_odds, total_odds = {}, {}, {}
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
                    spread_odds['market_id'] = market_id
                    spread_odds['game_total'] = outcomes[0].get('total')
                    spread_odds['game_over_odds'] = outcomes[0].get('odds_american')
                    spread_odds['game_under_odds'] = outcomes[1].get('odds_american')   

                elif market_name.lower().startswith("home total"):
                    # Extract spread odds
                    outcomes = book.get('outcomes', [])
                    spread_odds['market_id'] = market_id
                    spread_odds['home_total'] = outcomes[0].get('total')
                    spread_odds['home_over_odds'] = outcomes[0].get('odds_american')
                    spread_odds['home_under_odds'] = outcomes[1].get('odds_american') 

                elif market_name.lower().startswith("away total"):
                    # Extract spread odds
                    outcomes = book.get('outcomes', [])
                    spread_odds['market_id'] = market_id
                    spread_odds['away_total'] = outcomes[0].get('total')
                    spread_odds['away_over_odds'] = outcomes[0].get('odds_american')
                    spread_odds['away_under_odds'] = outcomes[1].get('odds_american')                              # Note: You'd need to adjust logic based on actual market structure for totals

    return winner_odds, spread_odds, total_odds
