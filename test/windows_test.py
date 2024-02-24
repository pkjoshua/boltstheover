import tkinter as tk
from tkinter import ttk
import pandas as pd
import sqlite3

db_path = 'assets/data.db'

def fetch_random_samples(db_path, table_name):
    """Fetch 5 random rows from the specified table."""
    with sqlite3.connect(db_path) as conn:
        query = f'SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 5'
        df = pd.read_sql_query(query, conn)
    return df

def display_in_window(dfs, table_names):
    """Display the DataFrames in a pop-up window with a horizontal scrollbar."""
    window = tk.Tk()
    window.title("Random Samples from Tables")

    frame = tk.Frame(window)
    frame.pack(fill='both', expand=True)

    # Create a canvas for adding scrollbars
    canvas = tk.Canvas(frame)
    canvas.pack(side='left', fill='both', expand=True)

    # Add a scrollbar
    scrollbar = ttk.Scrollbar(frame, orient='horizontal', command=canvas.xview)
    scrollbar.pack(side='bottom', fill='x')
    canvas.configure(xscrollcommand=scrollbar.set)

    # Add a frame inside the canvas for the tables
    table_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor='nw')

    # Populate the table frame with data from each DataFrame
    row_offset = 0
    for df, table_name in zip(dfs, table_names):
        tk.Label(table_frame, text=f"Table: {table_name}", font=('Arial', 16, 'bold')).grid(row=row_offset, column=0, columnspan=len(df.columns))
        row_offset += 1
        for (i, column) in enumerate(df.columns):
            tk.Label(table_frame, text=column, borderwidth=2, relief='ridge').grid(row=row_offset, column=i, sticky='nsew')
        row_offset += 1
        for (i, row) in df.iterrows():
            for (j, value) in enumerate(row):
                tk.Label(table_frame, text=value, borderwidth=2, relief='ridge').grid(row=row_offset+i, column=j, sticky='nsew')
        row_offset += len(df) + 1  # Extra offset for spacing between tables

    # Update the canvas's scrollregion to encompass the table frame
    table_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox('all'))

    window.mainloop()

def main():
    tables_to_examine = ['teams', 'schedule','team_stats_per_game', 'winner_odds', 'spread_odds', 'total_odds', 'home_total_odds', 'away_total_odds']
    dfs = [fetch_random_samples(db_path, table_name) for table_name in tables_to_examine]
    display_in_window(dfs, tables_to_examine)

if __name__ == "__main__":
    main()
