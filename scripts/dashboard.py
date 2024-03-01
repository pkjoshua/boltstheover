from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML template with inline CSS for the dashboard
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
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    team_name = None  # Initialize team_name
    if request.method == 'POST':
        team_name = request.form['teamName']
        with open('team_name.txt', 'w') as f:
            f.write(team_name)
        print(f"Team Name Entered: {team_name}")  # Example of what you might do
    return render_template_string(HTML_TEMPLATE, team_name=team_name)

if __name__ == '__main__':
    app.run(debug=True)
