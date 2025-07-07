import requests
from bs4 import BeautifulSoup
import csv

def extract_team_abbreviation(href):
    # Extract the team abbreviation part of the URL
    parts = href.split('/')
    if len(parts) > 2:
        team_abbr = parts[-2]  # The abbreviation is the second last part of the URL
        return team_abbr.upper()  # Convert to uppercase to standardize
    return "UNK"  # Unknown team abbreviation

def fetch_schedule(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    schedule_rows = soup.find_all('tr', class_=['Table__TR Table__TR--sm Table__even', 'filled Table__TR Table__TR--sm Table__even'])[1:]  # Skipping header row

    schedule_data = []
    for row in schedule_rows:
        cols = row.find_all('td')
        if len(cols) >= 6:
            game_date = cols[0].text.strip()
            home_away = "Home" if "vs" in cols[1].text else "Away"

            opponent_a_tag = cols[1].find('a')
            if opponent_a_tag:
                opponent_href = opponent_a_tag.get('href', '')
                opponent_abbr = extract_team_abbreviation(opponent_href)  # Use the new function here

                opponent = opponent_abbr  # Now directly using the abbreviation
            else:
                opponent = "UNK"

            result = f"{cols[2].find('span', class_='fw-bold').text.strip()} {cols[2].find('a').text.strip()}"
            record = cols[3].text.strip()
            goalie = cols[4].text.strip()
            top_performer = cols[5].text.strip()

            schedule_data.append({
                'Date': game_date,
                'Home/Away': home_away,
                'Opponent': opponent,
                'Result': result,
                'Record': record,
                'Goalie': goalie,
                'Top Performer': top_performer
            })

    return schedule_data

def save_to_csv(data, file_name):
    headers = ['Date', 'Home/Away', 'Opponent', 'Result', 'Record', 'Goalie', 'Top Performer']
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

url = 'https://www.espn.com/nhl/team/schedule/_/name/tb/tampa-bay-lightning'
schedule_data = fetch_schedule(url)
if schedule_data:
    save_to_csv(schedule_data, 'tampa_bay_lightning_schedule.csv')
else:
    print("No schedule data found.")
