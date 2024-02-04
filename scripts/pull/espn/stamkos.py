import requests
from bs4 import BeautifulSoup

def fetch_player_stats(player_id):
    url = f"https://www.espn.com/nhl/player/gamelog/_/id/{player_id}"
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
    game_rows = soup.find_all('tr', class_='Table__TR Table__TR--sm Table__even')

    player_stats = []

    for row in game_rows:
        cols = row.find_all('td')
        if len(cols) > 16:  # Adjust based on the expected number of columns for a complete data row
            try:
                stats = {
                    'Date': cols[0].text.strip(),
                    'Opponent': cols[1].text.strip(),
                    'Result': cols[2].text.strip(),
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
                    'Production Time': cols[16].text.strip() if len(cols) > 16 else 'N/A',  # Conditional based on column existence
                }
                player_stats.append(stats)
            except IndexError as e:
                print(f"Error processing a row, skipping it: {e}")
                continue  # Skip rows that don't match the expected structure
        else:
            print(f"Skipping a row with insufficient columns: found {len(cols)} columns")

    return player_stats


def save_stats_to_file(stats, file_name):
    try:
        with open(file_name, 'w') as file:
            for stat in stats:
                stat_line = ', '.join([f"{key}: {value}" for key, value in stat.items()])
                file.write(stat_line + '\n')
        print(f"Stats successfully saved to {file_name}")
    except IOError as e:
        print(f"Failed to write to file: {e}")

player_id = '5037'  # Example with Steven Stamkos
player_stats = fetch_player_stats(player_id)

if player_stats:
    save_stats_to_file(player_stats, f'stamkos_stats_{player_id}.txt')
else:
    print("No stats data to save.")
