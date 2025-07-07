import requests

def fetch_team_data(team_id):
    """
    Fetch data for a given team using the ESPN API.
    """
    url = f"https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/teams/{team_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to retrieve data. Status code: {response.status_code}")

def save_data_to_file(data, file_name):
    """
    Save the extracted 'record' and 'stats' data to a text file.
    """
    with open(file_name, 'w') as file:
        # Navigate to the 'record' object inside 'team'
        if 'team' in data and 'record' in data['team'] and 'items' in data['team']['record']:
            for item in data['team']['record']['items']:
                # Write record description, type, and summary
                file.write(f"Description: {item.get('description', 'N/A')}\n")
                file.write(f"Type: {item.get('type', 'N/A')}\n")
                file.write(f"Summary: {item.get('summary', 'N/A')}\n")

                # Write each stat in the 'stats' array
                if 'stats' in item:
                    for stat in item['stats']:
                        file.write(f"{stat.get('name', 'N/A')}: {stat.get('value', 'N/A')}\n")
                file.write("\n")

def main():
    team_id = '20'  # Tampa Bay Lightning team ID
    try:
        team_data = fetch_team_data(team_id)
        save_data_to_file(team_data, 'tampa_bay_lightning_stats.txt')
        print("Data saved to tampa_bay_lightning_stats.txt")
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()
