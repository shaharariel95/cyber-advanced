from flask import Flask, render_template, request, redirect, url_for, flash, make_response, session, jsonify
import requests
from flask_cors import CORS, cross_origin
from urllib.parse import urlparse
import json
from datetime import datetime
import hashlib

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = 'supersecretkey'

def generate_session_id(username):
    return hashlib.sha256(username.encode()).hexdigest()

@app.route('/')
@cross_origin()
def home():
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect(url_for('login'))
    
    with open('cred.json', 'r') as file:
        data = json.load(file)
    
    username = None
    for key, value in data['users'].items():
        if generate_session_id(value) == session_id:
            username = value
            break
    
    if not username:
        return redirect(url_for('login'))
    
    current_date = datetime.now().strftime("%B %d, %Y")
    
    with open('chat.json', 'r') as file:
        chat_data = json.load(file)
    
    chat_data = sorted(chat_data, key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('home.html', username=username, current_date=current_date, chat_data=chat_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    session_id = request.cookies.get('session_id')
    if session_id:
        with open('cred.json', 'r') as file:
            data = json.load(file)
        
        for key, value in data['users'].items():
            if generate_session_id(value) == session_id:
                resp = make_response(redirect(url_for('home')))
                resp.set_cookie('session_id', session_id)
                return resp

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with open('cred.json', 'r') as file:
            data = json.load(file)
        user_key = None
        for key, value in data['users'].items():
            if value == username:
                user_key = key
                break
        if user_key is None:
            flash('Username not correct')
        elif data['pass'][user_key] != password:
            flash('Password not correct')
        else:
            session_id = generate_session_id(username)
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('session_id', session_id)
            resp.set_cookie('name', username)
            return resp
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.set_cookie('session_id', '', expires=0)
    return resp

@app.route('/chat', methods=['POST'])
def chat():
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect(url_for('login'))
    
    with open('cred.json', 'r') as file:
        data = json.load(file)
    
    username = None
    for key, value in data['users'].items():
        if generate_session_id(value) == session_id:
            username = value
            break
    
    if not username:
        return redirect(url_for('login'))
    message = request.form['message']
    with open('chat.json', 'r') as file:
        chat_data = json.load(file)
    chat_data.append({"username": username, "message": message, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    with open('chat.json', 'w') as file:
        json.dump(chat_data, file)
    return redirect(url_for('home'))

  
@app.route('/delete_message', methods=['POST'])
def delete_message():
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect(url_for('login'))
    
    with open('cred.json', 'r') as file:
        data = json.load(file)
    
    username = None
    for key, value in data['users'].items():
        if generate_session_id(value) == session_id:
            username = value
            break
    
    if not username:
        return redirect(url_for('login'))
    
    timestamp = request.form['timestamp']
    
    with open('chat.json', 'r') as file:
        chat_data = json.load(file)
    
    chat_data = [msg for msg in chat_data if not (msg['timestamp'] == timestamp and msg['username'] == username)]
    
    with open('chat.json', 'w') as file:
        json.dump(chat_data, file)
    
    return redirect(url_for('home'))
  
# Add the new check user status endpoint
@app.route('/check_user_exists', methods=['GET'])
def check_user_exists():
    username = request.args.get('username')
    with open('cred.json', 'r') as file:
        data = json.load(file)
        users = data['users'].values()

    if username in users:
        return jsonify({'exists': True, 'username': username})
    else:
        return jsonify({'exists': False, 'username': username})

# Internal admin interface
@app.route('/admin')
def admin():
    with open('cred.json', 'r') as file:
        data = json.load(file)
    users = {key: value for key, value in data['users'].items() if key != "0"}
    return render_template('admin.html', users=users)

@app.route('/admin/delete', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        username = request.form['username']
    elif request.method == 'GET':
        username = request.args.get('username')

    if username == 'admin':
        flash('Admin cannot delete themselves.')
        return redirect(url_for('admin'))

    with open('cred.json', 'r') as file:
        data = json.load(file)

    users = data['users']
    passes = data['pass']
    user_key = None
    for key, value in users.items():
        if value == username:
            user_key = key
            break

    if user_key:
        del users[user_key]
        del passes[user_key]
        with open('cred.json', 'w') as file:
            json.dump({"users": users, "pass": passes}, file)
        flash(f"User {username} deleted successfully.")
    else:
        flash(f"User {username} not found.")
    return redirect(url_for('admin'))

def fetch_data_from_url(url):
    response = requests.get(url)
    return response.json()

@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    session_id = request.cookies.get('session_id')
    if not session_id:
        return redirect(url_for('login'))
    
    with open('cred.json', 'r') as file:
        data = json.load(file)
    
    username = None
    for key, value in data['users'].items():
        if generate_session_id(value) == session_id:
            username = value
            break
            
    url = request.form['url']
    try:
        data = fetch_data_from_url(url)
        return jsonify(data)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except requests.RequestException as e:
        return jsonify({'error': 'Failed to fetch data'}), 500

if __name__ == '__main__':
    app.run(debug=True)
