import requests
import sqlite3
import re  # Import the regex module for regular expressions

# API URL
api_url = "http://api.sportradar.us/nhl/trial/v7/en/league/hierarchy.json?api_key=3s2jrxegxx8b7eqa6nay9898"

# Function to extract numerical part from sr_id
def extract_number(sr_id):
    """Extracts numerical part from sr_id string."""
    match = re.search(r'\d+', sr_id)
    return match.group(0) if match else sr_id

# Fetch the data from the API
response = requests.get(api_url)
if response.status_code == 200:
    data = response.json()
else:
    print(f"Failed to fetch data: HTTP {response.status_code}")
    exit()

# Database path
db_path = 'assets/data.db'

# Connect to the SQLite database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Extract and insert league information
league_id = data['league']['id']

# Extract and insert conference, division, and team information
for conference in data['conferences']:
    conference_id = conference['id']
    conference_name = conference['name']
    
    for division in conference['divisions']:
        division_id = division['id']
        division_name = division['name']
        
        for team in division['teams']:
            global_team_id = team['id']
            name = team['name']
            market = team['market']
            alias = team['alias']
            team_id = extract_number(team.get('sr_id', ''))  # Extract number from sr_id
            
            # Insert data into the teams table
            c.execute('''
                INSERT INTO teams (league_id, conference_id, conference_name, division_id, division_name, global_team_id, team_id, name, alias) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (league_id, conference_id, conference_name, division_id, division_name, global_team_id, team_id, name, alias))

# Commit the changes and close the database connection
conn.commit()
conn.close()

print("Team roster data has been successfully inserted into the database.")
