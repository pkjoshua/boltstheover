import subprocess
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_path):
    """Runs a Python script located at the given path."""
    try:
        result = subprocess.run(['python3', script_path], check=True, text=True, capture_output=True)
        print(f"Successfully ran {script_path}:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}:")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        print(e.output)

def main():
    scripts_dir = os.path.join(os.getcwd(), 'scripts')  # Assuming the current working directory is the base directory

    schedule = os.path.join(scripts_dir, 'schedule.py')
    game_stats = os.path.join(scripts_dir, 'game_stats.py')
    event_odds = os.path.join(scripts_dir, 'event_odds.py')
    bet_suggest = os.path.join(scripts_dir, 'bet_suggest.py')


# Wait for 5 seconds
    run_script(schedule)
    time.sleep(2)  # Wait for 5 seconds
    run_script(game_stats)
    time.sleep(2)
    run_script(event_odds)
    time.sleep(2)
    run_script(bet_suggest)
    logging.info("Suggestion created.")


if __name__ == "__main__":
    main()
