import subprocess
import os
import logging 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_rigthenhl():
    # Define the path to the updater.py script
    # Assuming the 'scripts' directory is at the same level as initialize.py
    script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'build.py')
    
    # Use subprocess to run the script
    result = subprocess.run(['python3', script_path], capture_output=True, text=True)
    logging.info("Building Database...")
    # Print the output and error (if any)
    print("Output:", result.stdout)
    
    if result.stderr:
        print("Error:", result.stderr)
        logging.info("Initialization failed")

if __name__ == '__main__':
    initialize_rigthenhl()
