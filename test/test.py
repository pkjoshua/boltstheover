import pandas as pd
import sqlite3

db_path = 'assets/data.db'

def fetch_random_samples(db_path, table_name):
    """Fetch 5 random rows from the specified table."""
    with sqlite3.connect(db_path) as conn:
        query = f'SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 5'
        df = pd.read_sql_query(query, conn)
    return df

def display_in_terminal(dfs, table_names):
    """Display the DataFrames in the terminal with limited columns."""
    for df, table_name in zip(dfs, table_names):
        print(f"\nTable: {table_name}")

        # Determine how many columns to display at once based on the terminal width
        max_columns = 8  # Adjust this number based on your preference/terminal width

        if len(df.columns) <= max_columns:
            print(df.to_string(index=False))
        else:
            # If there are more columns than max_columns, display in chunks
            for start_col in range(0, len(df.columns), max_columns):
                end_col = min(start_col + max_columns, len(df.columns))
                print(df.iloc[:, start_col:end_col].to_string(index=False))
                if end_col < len(df.columns):
                    print("\n-- More --")  # Indicate that there's more data

def main():
    tables_to_examine = ['teams', 'schedule', 'team_stats_per_game','winner_odds','spread_odds','total_odds', 'home_total_odds', 'away_total_odds']
    dfs = [fetch_random_samples(db_path, table_name) for table_name in tables_to_examine]
    display_in_terminal(dfs, tables_to_examine)

if __name__ == "__main__":
    main()
