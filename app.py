from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import pymysql

app = Flask(__name__)
app.secret_key = 'super_secret_social_key'  # Needed for session storage
CORS(app)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'H@rsh1577',  # Change to your MySQL password
    'database': 'friend_db',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

# Ensure messages table exists for interaction
def init_chat_table():
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sender_id INT,
                receiver_id INT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sender_id) REFERENCES users(id),
                FOREIGN KEY (receiver_id) REFERENCES users(id)
            );
        """)
        conn.commit()
    conn.close()

init_chat_table()

# Routes to serve HTML pages
@app.route('/')
def auth_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard_page'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard_page():
    if 'user_id' not in session:
        return redirect(url_for('auth_page'))
    return render_template('dashboard.html')

# API Endpoints
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username, email, interests = data.get('username'), data.get('email'), data.get('interests', [])
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
            user_id = cursor.lastrowid
            for interest in interests:
                cursor.execute("INSERT INTO user_interests (user_id, interest) VALUES (%s, %s)", (user_id, interest))
            conn.commit()
        conn.close()
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({'status': 'success', 'user_id': user_id, 'username': username})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    try:
        conn = get_db()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, username FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify({'status': 'success', 'user_id': user['id'], 'username': user['username']})
        return jsonify({'status': 'error', 'message': 'User not found. Please register.'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'status': 'success'})

@app.route('/api/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'status': 'error'}), 401
    return jsonify({'user_id': session['user_id'], 'username': session['username']})

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    user_id = session.get('user_id')
    conn = get_db()
    with conn.cursor() as cursor:
        query = """
            SELECT DISTINCT u.id, u.username 
            FROM users u
            JOIN user_interests ui ON u.id = ui.user_id
            WHERE ui.interest IN (SELECT interest FROM user_interests WHERE user_id = %s)
            AND u.id != %s
            AND u.id NOT IN (
                SELECT user_id2 FROM friendships WHERE user_id1 = %s
                UNION
                SELECT user_id1 FROM friendships WHERE user_id2 = %s
            )
        """
        cursor.execute(query, (user_id, user_id, user_id, user_id))
        recs = cursor.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'recommendations': recs})

@app.route('/api/connect', methods=['POST'])
def connect():
    user_id = session.get('user_id')
    friend_id = request.get_json().get('friend_id')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO friendships (user_id1, user_id2, status) VALUES (%s, %s, 'accepted')", (user_id, friend_id))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/friends', methods=['GET'])
def get_friends():
    user_id = session.get('user_id')
    conn = get_db()
    with conn.cursor() as cursor:
        query = """
            SELECT u.id, u.username FROM users u
            WHERE u.id IN (
                SELECT user_id2 FROM friendships WHERE user_id1 = %s
                UNION
                SELECT user_id1 FROM friendships WHERE user_id2 = %s
            )
        """
        cursor.execute(query, (user_id, user_id))
        friends = cursor.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'friends': friends})

@app.route('/api/messages/<int:friend_id>', methods=['GET'])
def get_messages(friend_id):
    user_id = session.get('user_id')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT sender_id, message, timestamp FROM messages
            WHERE (sender_id = %s AND receiver_id = %s) OR (sender_id = %s AND receiver_id = %s)
            ORDER BY timestamp ASC
        """, (user_id, friend_id, friend_id, user_id))
        msgs = cursor.fetchall()
    conn.close()
    return jsonify({'status': 'success', 'messages': msgs})

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    user_id = session.get('user_id')
    data = request.get_json()
    receiver_id, msg = data.get('receiver_id'), data.get('message')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO messages (sender_id, receiver_id, message) VALUES (%s, %s, %s)", (user_id, receiver_id, msg))
        conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)