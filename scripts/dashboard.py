from flask import Flask, request, render_template_string, Response, jsonify, redirect, url_for
from threading import Thread
import subprocess
import time
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Global variable to store the current status and the timestamp for the last stats update
current_status = "Idle"
last_update_time = time.time()

# Updated HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NHL Betting Odds Dashboard</title>
    <style>
        body { background-color: #000; color: #fff; font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: auto; padding: 20px; }
        .form-group { margin-bottom: 20px; }
        label, .stats, #status-updates { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="submit"] { width: 100%; padding: 10px; margin-bottom: 10px; }
        input[type="submit"] { background-color: #00f; color: #fff; border: none; cursor: pointer; }
        input[type="submit"]:hover { background-color: #009; }
        #status, #stats-content { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="container">
        <div id="status-updates">
            <h3>Status Updates</h3>
            <pre id="status">Idle</pre>
        </div>
        <h2>NHL Team Name Input</h2>
        <form method="POST">
            <div class="form-group">
                <label for="teamName">Enter NHL Team Name:</label>
                <input type="text" id="teamName" name="teamName" required>
            </div>
            <input type="submit" value="Submit">
        </form>
        <div class="stats">
            <h3>Stats and Odds</h3>
            <pre id="stats-content"></pre>
        </div>
    </div>

    <script type="text/javascript">
    document.addEventListener("DOMContentLoaded", function() {
        var statusSource = new EventSource("/status");
        statusSource.onmessage = function(event) {
            document.getElementById("status").textContent = event.data;
        };

        // Fetch initial stats on page load
        fetchStats();

        // Function to fetch stats and update the page
        function fetchStats() {
            fetch("/stats")
                .then(response => response.json())
                .then(data => {
                    document.getElementById("stats-content").textContent = data.content;
                })
                .catch(error => console.error("Error fetching stats:", error));
        }

        // Periodically check for new stats every 5 seconds
        setInterval(fetchStats, 5000);
    });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        team_name = request.form['teamName'].title()  # Capitalize the team name properly
        # Start the stats and odds update process
        thread = Thread(target=run_script_async, args=(team_name,))
        thread.start()
        # Redirect to a new endpoint or the same endpoint to prevent re-execution on refresh
        return redirect(url_for('index'))
    else:
        return render_template_string(HTML_TEMPLATE)

def run_script_async(team_name):
    global current_status, last_update_time
    current_status = "Starting stats and odds update..."
    try:
        with open('team_name.txt', 'w') as f:
            f.write(team_name)
        # Simulate or run your long-running task
        subprocess.run(["python", "scripts/stats_and_odds.py"], check=True)
        current_status = "Stats and odds update completed."
        logging.info("Stats and odds update completed.")
    except subprocess.CalledProcessError as e:
        current_status = f"Error running script: {str(e)}"
    finally:
        last_update_time = time.time()

@app.route('/status')
def status():
    def generate():
        global current_status
        while True:
            yield f"data: {current_status}\n\n"
            time.sleep(1)
    return Response(generate(), mimetype='text/event-stream')

@app.route('/stats')
def stats():
    global last_update_time
    stats_content = ""
    updated = False
    try:
        stats_path = 'betting_stats.txt'
        if os.path.exists(stats_path):
            with open(stats_path, 'r') as file:
                stats_content = file.read()
                file_time = os.path.getmtime(stats_path)
                if file_time > last_update_time:
                    updated = True
                    last_update_time = file_time
                    logging.info("Stats and odds updated.")
    except Exception as e:
        stats_content = f"Error loading stats: {str(e)}"
        logging.info("Error loading stats")
    return jsonify({'content': stats_content, 'updated': updated})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

