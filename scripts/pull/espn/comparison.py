import requests
import matplotlib.pyplot as plt

# Constants for team IDs
TAMPA_BAY_LIGHTNING_ID = '20'
FLORIDA_PANTHERS_ID = '26'

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

def extract_stats(data):
    """
    Extract relevant stats from the team data.
    """
    stats_dict = {}
    if 'team' in data and 'record' in data['team'] and 'items' in data['team']['record']:
        for item in data['team']['record']['items']:
            if item.get('type') == 'total':
                for stat in item['stats']:
                    stats_dict[stat['name']] = stat['value']
    return stats_dict

def create_comparison_chart(stats1, stats2, team1_name, team2_name):
    """
    Create a comparison chart between two teams.
    """
    labels = list(stats1.keys())
    team1_values = [stats1[label] for label in labels]
    team2_values = [stats2[label] for label in labels]

    x = range(len(labels))
    fig, ax = plt.subplots()
    bar_width = 0.35

    bars1 = ax.bar([pos - bar_width/2 for pos in x], team1_values, width=bar_width, label=team1_name)
    bars2 = ax.bar([pos + bar_width/2 for pos in x], team2_values, width=bar_width, label=team2_name)

    ax.set_xlabel('Statistic')
    ax.set_ylabel('Value')
    ax.set_title('Team Statistics Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45)
    ax.legend()

    # Adding the values on the bars
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate('{}'.format(round(height, 2)),
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

def main():
    try:
        tampa_data = fetch_team_data(TAMPA_BAY_LIGHTNING_ID)
        tampa_stats = extract_stats(tampa_data)
        
        panthers_data = fetch_team_data(FLORIDA_PANTHERS_ID)
        panthers_stats = extract_stats(panthers_data)

        create_comparison_chart(tampa_stats, panthers_stats, 'Tampa Bay Lightning', 'Florida Panthers')
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()
