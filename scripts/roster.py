import requests
from bs4 import BeautifulSoup
import csv

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
    current_position = "Unknown"
    players_data = []

    # Position abbreviations
    position_map = {
        'Centers': 'C',
        'Left Wings': 'LW',
        'Right Wings': 'RW',
        'Defense': 'D',
        'Goalies': 'G'
    }

    roster_elements = soup.find_all(['tr', 'div'], class_=['Table__TR Table__TR--lg Table__even', 'Table__Title'])

    for element in roster_elements:
        if element.name == 'div' and 'Table__Title' in element['class']:
            # Map the full position name to its abbreviation
            current_position = position_map.get(element.text, "Unknown")
        elif element.name == 'tr':
            cols = element.find_all('td')
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
                    'shot': cols[5].text.strip(),
                    'position': current_position  # Use the abbreviated position
                }
                players_data.append(player_info)

    return players_data

def save_to_csv(players_data, file_name):
    headers = ['id', 'name', 'position', 'jersey_number', 'age', 'height', 'weight', 'shot']

    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for player in players_data:
            writer.writerow(player)

    print(f"Data successfully saved to {file_name}")

url = 'https://www.espn.com/nhl/team/roster/_/name/tb/tampa-bay-lightning'
players_data = fetch_roster_data(url)
if players_data:
    save_to_csv(players_data, 'tampa_bay_lightning_roster.csv')
else:
    print("No data to save.")
