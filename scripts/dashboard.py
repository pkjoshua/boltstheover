from flask import Flask, request, render_template_string, redirect, url_for, jsonify
from threading import Thread
import subprocess
import os

app = Flask(__name__)

# Flag to indicate if stats are updated
stats_updated = False

# Updated HTML_TEMPLATE with stats_content display
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NHL Betting Odds Dashboard</title>
    <style>
        body { background-color: #000; color: #fff; font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: auto; padding: 20px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"] { width: 100%; padding: 10px; margin-bottom: 10px; }
        input[type="submit"] { padding: 10px 20px; background-color: #00f; color: #fff; border: none; cursor: pointer; }
        input[type="submit"]:hover { background-color: #009; }
        .stats pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<script>
    function checkForUpdates() {
        fetch('/check-updates')
            .then(response => response.json())
            .then(data => {
                if (data.updated) {
                    window.location.reload(true); // Force reload to fetch new stats
                } else {
                    setTimeout(checkForUpdates, 5000); // Check again in 5 seconds
                }
            })
            .catch(error => console.error('Error checking for updates:', error));
    }

    // Start polling for updates after the page loads
    window.onload = function() {
        setTimeout(checkForUpdates, 5000);
    };
</script>
<body>
    <div class="container">
        <h2>NHL Team Name Input</h2>
        <form method="POST">
            <div class="form-group">
                <label for="teamName">Enter NHL Team Name:</label>
                <input type="text" id="teamName" name="teamName" required>
            </div>
            <input type="submit" value="Submit">
        </form>
        {% if team_name %}
            <h3>You entered: {{ team_name }}</h3>
        {% endif %}
        {% if stats_content %}
        <div class="stats">
            <h3>Stats and Odds</h3>
            <pre>{{ stats_content }}</pre>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

def run_script_async(team_name):
    """Run the stats script asynchronously and update the stats flag."""
    global stats_updated
    with open('team_name.txt', 'w') as f:
        f.write(team_name)
    subprocess.run(["python", "scripts/stats_and_odds.py"], check=True)
    # After script finishes, update the flag
    stats_updated = True

@app.route('/', methods=['GET', 'POST'])
def index():
    global stats_updated
    if request.method == 'POST':
        team_name = request.form['teamName'].title()
        # Reset the update flag on new POST request
        stats_updated = False
        thread = Thread(target=run_script_async, args=(team_name,))
        thread.start()
        return redirect(url_for('index'))
    else:
        team_name = None
        stats_content = ""
        try:
            with open('betting_stats.txt', 'r') as file:
                stats_content = file.read()
        except FileNotFoundError:
            pass
        return render_template_string(HTML_TEMPLATE, team_name=team_name, stats_content=stats_content)

@app.route('/check-updates')
def check_updates():
    """Endpoint to check if the stats have been updated."""
    global stats_updated
    if stats_updated:
        # Reset the flag before response
        stats_updated = False
        return jsonify({'updated': True})
    else:
        return jsonify({'updated': False})

if __name__ == '__main__':
    app.run(debug=True)