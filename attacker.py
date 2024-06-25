from flask import Flask, request, render_template_string, make_response
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})

def read_session_ids():
    try:
        with open('session.txt', 'r') as f:
            session_ids = f.read().splitlines()
    except FileNotFoundError:
        session_ids = []
    return session_ids

def write_session_ids(session_ids):
    with open('session.txt', 'w') as f:
        for session_id in session_ids:
            f.write(f"{session_id}\n")

@app.route('/CSRFCookie', methods=['POST'])
def csrf_cookie():
    session_id = request.form.get('session_id')
    session_ids = read_session_ids()
    
    if session_id and session_id not in session_ids:
        session_ids.append(session_id)
        write_session_ids(session_ids)
    
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@app.route('/')
@cross_origin()
def home():
    session_ids = read_session_ids()
    
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
      <p>Session IDs:</p>
      <ul>
        {% for session_id in session_ids %}
          <li>{{ session_id }}</li>
        {% endfor %}
      </ul>
    </body>
    </html>
    """
    
    return render_template_string(html, session_ids=session_ids)

if __name__ == '__main__':
    app.run(port=8080)
