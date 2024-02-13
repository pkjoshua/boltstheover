import requests
import pandas as pd

def fetch_json_from_api(url):
    """Fetch JSON data from the provided API URL."""
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: HTTP {response.status_code}")
        return None

def normalize_json_to_table(json_data, output_file):
    """Normalize JSON data into pandas DataFrame (table format) and save to a file."""
    if json_data:
        df = pd.json_normalize(json_data)
        # Save the DataFrame to a CSV file
        df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
    else:
        print("No data to normalize.")

def main(api_url, output_file):
    """Main function to fetch JSON from API, normalize it into a table, and save the table to a file."""
    json_data = fetch_json_from_api(api_url)
    normalize_json_to_table(json_data, output_file)

if __name__ == "__main__":
    api_url = 'https://api.sportradar.us/oddscomparison-ust1/en/us/sports/sr:sport:4/2024-02-12/schedule.json?api_key=65y54ktqk5v56gv9vqa7smp7'  # Replace with your actual API URL
    output_file = 'normalized_data.csv'  # Specify your desired output file name
    main(api_url, output_file)
