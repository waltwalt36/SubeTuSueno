from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_socketio import join_room, leave_room, send, SocketIO
from API import chatbot_response
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app)  # Initialize Socket.IO

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''
    CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL)
    ''')
    conn.commit()
    conn.close()

# Call this function when your app starts
init_db()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please fill in all fields', 'error-fields')
            return redirect(url_for('login'))

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('homepage'))
        else:
            flash('Invalid username or password', 'error-invalid')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email', '')  # Get email if provided

        if not username or not password or not email:
            flash('Please fill in all fields', 'error-fields')
            return redirect(url_for('signin'))

        hashed_password = generate_password_hash(password)

        try:
            with sqlite3.connect('users.db', check_same_thread=False) as conn:
                c = conn.cursor()
                c.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)', 
                          (username, hashed_password, email))
                conn.commit()
            # flash('User registered successfully!')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists. Please choose a different one.')
            return redirect(url_for('signin'))

    return render_template('signup.html')

@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    return render_template('homepage.html')

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('prompt')  # Get the prompt from the request
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    bot_reply = chatbot_response(user_input)  # Call the chatbot function
    return jsonify({'response': bot_reply})  # Return the response as JSON

# Live chat room route
@app.route("/room", methods=["GET", "POST"])
def room():
    if request.method == "POST":
        # Render the room.html template on POST
        return render_template("room.html")
    # Handle GET requests (optional)
    return render_template("room.html")

# Socket.IO events for live chat
@socketio.on("join")
def on_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    send(f"{username} has joined the room.", to=room)

@socketio.on("leave")
def on_leave(data):
    username = data["username"]
    room = data["room"]
    leave_room(room)
    send(f"{username} has left the room.", to=room)

@socketio.on("message")
def on_message(data):
    room = data["room"]
    message = data["message"]
    send(message, to=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)