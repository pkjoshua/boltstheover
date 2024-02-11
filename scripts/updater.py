import subprocess
import os

def run_script(script_path):
    """Runs a Python script located at the given path."""
    try:
        result = subprocess.run(['python3', script_path], check=True, text=True, capture_output=True)
        print(f"Successfully ran {script_path}:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_path}:")
        print(e.output)

def main():
    scripts_dir = os.path.join(os.getcwd(), 'scripts')  # Assuming the current working directory is the base directory

    # Define the paths to the scripts
    schedule_script_path = os.path.join(scripts_dir, 'schedule.py')
    player_stats_script_path = os.path.join(scripts_dir, 'player_stats_per_game.py')

    # Run the scripts in sequence
    run_script(schedule_script_path)
    run_script(player_stats_script_path)

if __name__ == "__main__":
    main()
