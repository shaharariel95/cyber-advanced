from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_cors import CORS, cross_origin
import json
import random
import string
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})
# app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = 'supersecretkey'




def generate_session_id(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route('/')
@cross_origin()
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
            session_id = generate_session_id()
            session['username'] = username
            resp = make_response(redirect(url_for('home')))
            resp.set_cookie('session_id', session_id)
            
            return resp
    
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
