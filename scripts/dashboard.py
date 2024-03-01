from flask import Flask, request, render_template_string
import subprocess

app = Flask(__name__)

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

@app.route('/', methods=['GET', 'POST'])
def index():
    team_name = None
    stats_content = ""
    if request.method == 'POST':
        team_name = request.form['teamName'].title()
        with open('team_name.txt', 'w') as f:
            f.write(team_name)
        subprocess.run(["python", "scripts/stats_and_odds.py"], check=True)
        with open('betting_stats.txt', 'r') as file:
            stats_content = file.read()
    return render_template_string(HTML_TEMPLATE, team_name=team_name, stats_content=stats_content)

if __name__ == '__main__':
    app.run(debug=True)
