import requests
from bs4 import BeautifulSoup
import csv
import os

def read_player_ids(csv_path='assets/team_rosters/nhl_roster.csv'):
    player_team_ids = []  # This will store both player and team IDs
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            player_team_ids.append((row['team_id'], row['player_id']))  # Change here to include TeamID
    return player_team_ids

def extract_game_id(result_link):
    if '/gameId/' in result_link:
        return result_link.split('/gameId/')[1].split('/')[0]
    return "N/A"

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

def save_stats_to_csv(all_player_stats, file_name='nhl_player_stats_2324.csv'):
    directory = 'assets/player_stats'
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, file_name)
    
    headers = ['team_id', 'player_id', 'game_id', 'date', 'opponent', 'result', 'score', 'goals', 'assists', 'points', 'plus_minus', 'penalty_minutes', 'shots', 'shot_percentage', 'pp_goals', 'pp_assists', 'sh_goals', 'sh_assists', 'gw_goals', 'toi', 'pt']
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for stat in all_player_stats:
            writer.writerow(stat)
            print(f"Stats successfully saved to {file_path}")

# Main execution
all_player_stats = []
player_team_ids = read_player_ids()

for team_player_id in player_team_ids:
    team_id, player_id = team_player_id  # Unpack the tuple here to access player_id
    player_stats = fetch_player_stats(team_player_id)
    all_player_stats.extend(player_stats)
    # Move the print statement inside the loop and after stats have been fetched
    print(f"Finished fetching stats for player ID {player_id}")

save_stats_to_csv(all_player_stats)