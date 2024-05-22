from flask import Flask, render_template, request, redirect, url_for, flash, session
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

if __name__ == '__main__':
    app.run(debug=True)
