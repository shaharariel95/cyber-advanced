from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
import json
from datetime import datetime
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'supersecretkey'


@app.route('/')
def home():
    if 'username' in session:
        username = session['username']
        current_date = datetime.now().strftime("%B %d, %Y")
        with open('chat.json', 'r') as file:
            chat_data = json.load(file)
        return render_template('home.html', username=username, current_date=current_date, chat_data=chat_data)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
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
            session['username'] = username
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/chat', methods=['POST'])
def chat():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    message = request.form['message']
    with open('chat.json', 'r') as file:
        chat_data = json.load(file)
    chat_data.append({"username": username, "message": message, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
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


@app.route('/admin')
def admin():
    if 'username' in session and session['username'] == 'admin':
        with open('cred.json', 'r') as file:
            data = json.load(file)
        
        users = {k: v for k, v in data['users'].items() if k != "0"}
        return render_template('admin.html', users=users)
    
    flash('Unauthorized access. Please log in as an admin.')
    return redirect(url_for('login'))


@app.route('/admin/delete', methods=['GET', 'POST'])
def delete_user():
    if request.method == 'POST':
        username = request.form['username']
        url = request.form.get('url', None)  # Allow admin to provide URL
        print (url)

        # Check if the URL is safe before making any requests
        if url and not is_url_whitelisted(url, WHITELISTED_URLS):
            flash('Invalid URL specified.')
            return redirect(url_for('admin'))
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


# Configuration for whitelisted URLs
WHITELISTED_URLS = [
    "https://api.example.com",
    "https://another-trusted-site.com"
]

def is_url_whitelisted(url, whitelist):
    parsed_url = urlparse(url)
    for allowed in whitelist:
        allowed_parsed = urlparse(allowed)
        if parsed_url.scheme == allowed_parsed.scheme and parsed_url.netloc == allowed_parsed.netloc:
            return True
    return False

def fetch_data_from_url(url):
    if not is_url_whitelisted(url, WHITELISTED_URLS):
        raise ValueError("URL not whitelisted")
    response = requests.get(url)
    return response.json()

@app.route('/fetch-data', methods=['POST'])
def fetch_data():
    if 'username' not in session:
        return redirect(url_for('login'))
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
