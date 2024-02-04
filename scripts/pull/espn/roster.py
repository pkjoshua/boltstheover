import requests
from bs4 import BeautifulSoup

def fetch_roster_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    player_rows = soup.find_all('tr', class_='Table__TR Table__TR--lg Table__even')
    players_data = []

    for row in player_rows:
        cols = row.find_all('td')
        if cols:
            player_link = cols[1].find('a')['href'] if cols[1].find('a') else ''
            player_id = player_link.split('/')[-1] if player_link else 'N/A'
            player_info = {
                'id': player_id,
                'name': cols[1].find('a').text.strip() if cols[1].find('a') else 'Unknown',
                'jersey_number': cols[1].find('span').text.strip() if cols[1].find('span') else 'N/A',
                'age': cols[2].text.strip(),
                'height': cols[3].text.strip(),
                'weight': cols[4].text.strip(),
                'shot': cols[5].text.strip()
            }
            players_data.append(player_info)
    return players_data

def save_to_file(players_data, file_name):
    try:
        with open(file_name, 'w') as file:
            for player in players_data:
                player_data = f"ID: {player['id']}, Name: {player['name']}, Jersey Number: {player['jersey_number']}, Age: {player['age']}, Height: {player['height']}, Weight: {player['weight']}, Shot: {player['shot']}\n"
                file.write(player_data)
        print(f"Data successfully saved to {file_name}")
    except IOError as e:
        print(f"Failed to write to file: {e}")

url = 'https://www.espn.com/nhl/team/roster/_/name/tb/tampa-bay-lightning'
players_data = fetch_roster_data(url)
if players_data:
    save_to_file(players_data, 'tampa_bay_lightning_roster_with_ids.txt')
else:
    print("No data to save.")
