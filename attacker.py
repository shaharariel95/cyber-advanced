from flask import Flask, request, redirect, url_for, render_template_string, make_response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5050"}})  # Only allow requests from port 5000
# app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/CSRFCookie', methods=['POST'])
# @cross_origin()
def csrf_cookie():
    session_id = request.form.get('session_id')
    if session_id:
        with open('session.txt', 'w') as f:
            f.write(session_id)
    
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response
            
@app.route('/')
@cross_origin()
def home():
    try:
        with open('session.txt', 'r') as f:
            session_id = f.readline()
    except FileNotFoundError:
        session_id = "No session ID set"
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Hello World</title>
      <style>
        body {
          background-color: darkgrey;
        }
        h1 {
          color: black;
        }
      </style>
    </head>
    <body>
      <h1>cookies!</h1>
      <img src='/static/cookie.png' width='256' height='256'>
      <p>Session ID: {{ session_id }}</p>
    </body>
    </html>
    """
    
    return render_template_string(html, session_id=session_id)

if __name__ == '__main__':
    app.run(port=8080)
