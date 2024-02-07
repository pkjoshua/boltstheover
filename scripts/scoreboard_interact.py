import requests

def fetch_nhl_scoreboard():
    url = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
    response = requests.get(url)
    data = response.json()  # Parse the JSON response
    return data

def extract_and_display_info(data):
    print("NHL Scoreboard\n")
    for event in data.get('events', []):
        game_id = event.get('id')
        competitions = event.get('competitions', [])
        
        for competition in competitions:
            competitors = competition.get('competitors', [])
            odds = competition.get('odds', [{}])[0]  # Assume single odds object
            
            print(f"Game ID: {game_id}")
            print("Teams:")
            for team in competitors:
                team_id = team.get('id')
                color = team.get('team', {}).get('color')
                alternate_color = team.get('team', {}).get('alternateColor')
                abbreviation = team.get('team', {}).get('abbreviation')
                print(f"  Team ID: {team_id}, Abbreviation: {abbreviation}, Color: {color}, Alternate Color: {alternate_color}")
            
            print("Odds:")
            details = odds.get('details')
            over_under = odds.get('overUnder')
            spread = odds.get('spread')
            print(f"  Details: {details}, Over/Under: {over_under}, Spread: {spread}\n")

def main():
    data = fetch_nhl_scoreboard()
    extract_and_display_info(data)

if __name__ == "__main__":
    main()
