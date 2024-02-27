import subprocess
import os
import time

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

    # Define the paths to the scripts
    create_database = os.path.join(scripts_dir, 'create_db.py')
    teams = os.path.join(scripts_dir, 'teams.py')
    schedule_script_path = os.path.join(scripts_dir, 'schedule.py')
    game_stats = os.path.join(scripts_dir, 'game_stats.py')

    # Run the scripts in sequence with a 5-second pause between each
    run_script(create_database)
    time.sleep(5)  # Wait for 5 seconds
    run_script(teams)
    time.sleep(5)  # Wait for 5 seconds
    run_script(schedule_script_path)
    time.sleep(5)  # Wait for 5 seconds
    run_script(game_stats)

if __name__ == "__main__":
    main()
