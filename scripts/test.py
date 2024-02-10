import sqlite3
import os

# Define the path to your SQLite database
db_path = os.path.join('assets', 'data.db')

def check_data_in_table(table_name):
    """Check and print a few rows from a specified table to verify data insertion."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"Checking data in the {table_name} table:")
    try:
        cursor.execute(f'SELECT * FROM {table_name} LIMIT 5')  # Retrieves 5 rows from the specified table
        rows = cursor.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print(f"No data found in the {table_name} table.")
    except sqlite3.Error as e:
        print(f"An error occurred when querying {table_name}: {e}")
    finally:
        conn.close()

# Check data in the roster, schedule, and player_stats tables
check_data_in_table('roster')
check_data_in_table('schedules')
check_data_in_table('player_stats')
