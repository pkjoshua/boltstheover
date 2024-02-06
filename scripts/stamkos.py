import requests
from bs4 import BeautifulSoup
import csv
import os

def read_player_ids(csv_path='assets/team_rosters/nhl_roster.csv'):
    player_ids = []
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            player_ids.append(row['id'])
    return player_ids

def extract_game_id(result_link):
    if '/gameId/' in result_link:
        return result_link.split('/gameId/')[1].split('/')[0]
    return "N/A"

def fetch_player_stats(player_id):
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
                'PlayerID': player_id,
                'GameID': game_id,
                'Date': cols[0].text.strip(),
                'Opponent': cols[1].text.strip(),
                'Result': win_loss,
                'Score': result_score,
                'Goals': cols[3].text.strip(),
                'Assists': cols[4].text.strip(),
                'Points': cols[5].text.strip(),
                '+/-': cols[6].text.strip(),
                'Penalty Minutes': cols[7].text.strip(),
                'Shots': cols[8].text.strip(),
                'Shot %': cols[9].text.strip(),
                'PP Goals': cols[10].text.strip(),
                'PP Assists': cols[11].text.strip(),
                'SH Goals': cols[12].text.strip(),
                'SH Assists': cols[13].text.strip(),
                'GW Goals': cols[14].text.strip(),
                'Time on Ice': cols[15].text.strip(),
                'Production Time': cols[16].text.strip() if len(cols) > 16 else 'N/A'
            }
            player_stats.append(stats)

    return player_stats
def save_stats_to_csv(all_player_stats, file_name='nhl_player_stats.csv'):
    directory = 'assets/player_stats'
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, file_name)
    
    # Define the CSV file column headers based on your stats dictionary keys
    headers = ['PlayerID', 'GameID', 'Date', 'Opponent', 'Result', 'Score', 'Goals', 'Assists', 'Points', '+/-', 'Penalty Minutes', 'Shots', 'Shot %', 'PP Goals', 'PP Assists', 'SH Goals', 'SH Assists', 'GW Goals', 'Time on Ice', 'Production Time']
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for stat in all_player_stats:
            writer.writerow(stat)
    print(f"Stats successfully saved to {file_path}")

# Main execution logic
all_player_stats = []
player_ids = read_player_ids()

for player_id in player_ids:
    player_stats = fetch_player_stats(player_id)
    all_player_stats.extend(player_stats)
    print(f"Finished fetching stats for player ID {player_id}")

save_stats_to_csv(all_player_stats)