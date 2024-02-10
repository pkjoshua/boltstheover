import requests
from bs4 import BeautifulSoup
import sqlite3
import os

db_path = os.path.join('assets', 'data.db')

def extract_game_id(result_link):
    if '/gameId/' in result_link:
        return result_link.split('/gameId/')[1].split('/')[0]
    return "N/A"

def fetch_player_ids_from_db():
    """Fetch player and team IDs from the roster table in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    player_team_ids = []

    try:
        cursor.execute('SELECT team_id, player_id FROM roster')
        player_team_ids = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"An error occurred while fetching player IDs: {e}")
    finally:
        conn.close()

    return player_team_ids

def insert_player_stats_into_db(all_player_stats):
    """Insert player statistics into the player_stats table in the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for stat in all_player_stats:
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO player_stats (team_id, player_id, game_id, date, opponent, result, score, goals, assists, points, plus_minus, penalty_minutes, shots, shot_percentage, pp_goals, pp_assists, sh_goals, sh_assists, gw_goals, toi, pt)
            VALUES (:team_id, :player_id, :game_id, :date, :opponent, :result, :score, :goals, :assists, :points, :plus_minus, :penalty_minutes, :shots, :shot_percentage, :pp_goals, :pp_assists, :sh_goals, :sh_assists, :gw_goals, :toi, :pt)
            ''', stat)
        except sqlite3.IntegrityError as e:
            print(f"SQLite Integrity Error: {e}, for player: {stat['player_id']}")
        except Exception as e:
            print(f"Unexpected error: {e}, for player: {stat['player_id']}")

    conn.commit()
    conn.close()
    print("Player stats data successfully inserted into the database.")

def fetch_player_stats(team_player_id):
    team_id, player_id = team_player_id  # Unpack the tuple
    url = f"https://www.espn.com/nhl/player/gamelog/_/id/{player_id}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    game_rows = soup.find_all('tr', class_='Table__TR Table__TR--sm Table__even') + \
                soup.find_all('tr', class_='filled Table__TR Table__TR--sm Table__even')

    player_stats = []

    for row in game_rows:
        cols = row.find_all('td')
        if len(cols) > 16:
            result_link = cols[2].find('a', href=True)
            game_id = extract_game_id(result_link['href']) if result_link else "N/A"
            win_loss = result_link.find('div', class_='ResultCell').text.strip() if result_link else "N/A"
            result_score = result_link.text.strip() if result_link else "N/A"
            
            stats = {
                'team_id': team_id, 
                'player_id': player_id,
                'game_id': game_id,
                'date': cols[0].text.strip(),
                'opponent': cols[1].text.strip(),
                'result': win_loss,
                'score': result_score,
                'goals': cols[3].text.strip(),
                'assists': cols[4].text.strip(),
                'points': cols[5].text.strip(),
                'plus_minus': cols[6].text.strip(),
                'penalty_minutes': cols[7].text.strip(),
                'shots': cols[8].text.strip(),
                'shot_percentage': cols[9].text.strip(),
                'pp_goals': cols[10].text.strip(),
                'pp_assists': cols[11].text.strip(),
                'sh_goals': cols[12].text.strip(),
                'sh_assists': cols[13].text.strip(),
                'gw_goals': cols[14].text.strip(),
                'toi': cols[15].text.strip(),
                'pt': cols[16].text.strip() if len(cols) > 16 else 'N/A'
            }
            player_stats.append(stats)

    return player_stats

# Main execution
all_player_stats = []
player_team_ids = fetch_player_ids_from_db()

for team_player_id in player_team_ids:
    team_id, player_id = team_player_id  # Unpack the tuple here to access player_id
    player_stats = fetch_player_stats(team_player_id)
    all_player_stats.extend(player_stats)
    # Print statement to indicate progress
    print(f"Finished fetching stats for player ID {player_id}")

insert_player_stats_into_db(all_player_stats)