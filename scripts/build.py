import subprocess
import os
import time
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_path):
    """Runs a Python script located at the given path."""
    try:
        result = subprocess.run(['python3', script_path], check=True, text=True, capture_output=True)
        logging.info(f"Successfully ran {script_path}:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}:")
        logging.info(f"Error running {script_path}:")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        print(e.output)

def main():
    scripts_dir = os.path.join(os.getcwd(), 'scripts')  # Assuming the current working directory is the base directory

    # Define the paths to the scripts
    create_database = os.path.join(scripts_dir, 'create_db.py')
    teams = os.path.join(scripts_dir, 'teams.py')
    schedule = os.path.join(scripts_dir, 'schedule.py')
    dashboard = os.path.join(scripts_dir, 'dashboard.py')

    # Run the scripts in sequence with a 5-second pause between each
    logging.info("Creating database")
    run_script(create_database)
    time.sleep(5)  # Wait for 5 seconds
    logging.info("Database created. Fetching teams")
    run_script(teams)
    time.sleep(5)  # Wait for 5 seconds
    logging.info("Teams fetched. Fetching the schedule")
    run_script(schedule)
    logging.info("Schedule fetched. Initializing dashboard")
    run_script(dashboard)
    
if __name__ == "__main__":
    main()
