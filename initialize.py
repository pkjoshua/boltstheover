import subprocess
import os

def start_updater_script():
    # Define the path to the updater.py script
    # Assuming the 'scripts' directory is at the same level as initialize.py
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'updater.py')
    
    # Use subprocess to run the script
    result = subprocess.run(['python', script_path], capture_output=True, text=True)
    
    # Print the output and error (if any)
    print("Output:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)

if __name__ == '__main__':
    start_updater_script()
