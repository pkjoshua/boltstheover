from flask import Flask, request, render_template_string, Response, redirect, url_for
from threading import Thread
import subprocess
import time

app = Flask(__name__)

# Global variable to store the current status - consider using a more robust solution for production
current_status = "Idle"

# HTML template with added section for status updates and SSE JavaScript
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
        input[type="text"], input[type="submit"] { width: 100%; padding: 10px; margin-bottom: 10px; }
        input[type="submit"] { background-color: #00f; color: #fff; border: none; cursor: pointer; }
        input[type="submit"]:hover { background-color: #009; }
        .stats pre, #status { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
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
        <div id="status-updates">
            <h3>Status Updates</h3>
            <pre id="status"></pre>
        </div>
    </div>

    <script type="text/javascript">
    document.addEventListener("DOMContentLoaded", function() {
        var source = new EventSource("/status");
        source.onmessage = function(event) {
            document.getElementById("status").textContent = event.data;
        };
    });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        team_name = request.form['teamName'].title()  # Capitalize the team name properly
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
            pass  # Handle the case where betting_stats.txt doesn't exist yet
        return render_template_string(HTML_TEMPLATE, team_name=team_name, stats_content=stats_content)

def run_script_async(team_name):
    global current_status
    current_status = "Starting stats and odds update..."
    with open('team_name.txt', 'w') as f:
        f.write(team_name)
    try:
        subprocess.run(["python", "scripts/stats_and_odds.py"], check=True)
        current_status = "Stats and odds update completed."
    except subprocess.CalledProcessError as e:
        current_status = f"Error: {str(e)}"
    time.sleep(1)  # Just to ensure the status update is seen by users

@app.route('/status')
def status():
    def generate():
        global current_status
        while True:
            yield f"data: {current_status}\n\n"
            time.sleep(1)  # Refresh the status every second
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)
