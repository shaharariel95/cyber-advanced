from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import requests
import json
from datetime import datetime

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
@app.route('/check-user-exists', methods=['POST'])
def check_user_exists():
    url = request.form.get('userApi')
    
    if not url:
        return jsonify({'exists': False, 'message': 'No URL provided'}), 400

    with open('cred.json', 'r') as file:
        data = json.load(file)
        users = data['users'].values()

    response = {
        'exists': False,
        'username': None
    }

    # Extract the username from the provided URL
    username = url.split('=')[-1]  # Assuming the URL format is fixed and ends with '=username'

    if username in users:
        response['exists'] = True
        response['username'] = username
    
    return jsonify(response)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
