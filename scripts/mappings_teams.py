import sqlite3

def query_teams():
    # Path to your SQLite database
    db_path = 'assets/data.db'

    # SQL query to select the specified fields from teams where the name matches the specified teams
    query = """
    SELECT global_team_id, team_id, name
    FROM teams
    """

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Execute the query
        cursor.execute(query)

        # Fetch all results
        results = cursor.fetchall()

        # Check if results were found
        if results:
            print("Query Results:")
            for row in results:
                print(f"Global Team ID: {row[0]}, Team ID: {row[1]}, Name: {row[2]}")
        else:
            print("No matching records found.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the connection to the database
        conn.close()

if __name__ == "__main__":
    query_teams()
