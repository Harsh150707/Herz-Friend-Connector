# # # import pymysql

# # # DB_CONFIG = {
# # #     'host': 'localhost',
# # #     'user': 'root',
# # #     'password': '',  # Update with your MySQL password if any
# # #     'database': 'friend_db',
# # #     'cursorclass': pymysql.cursors.DictCursor,
# # # }


# # # def setup_database():
# # #   # 1. Connect without database selected to create it if it doesn't exist
# # #   conn = pymysql.connect(
# # #       host=DB_CONFIG['host'], user=DB_CONFIG['user'], password=DB_CONFIG['password']
# # #   )
# # #   cursor = conn.cursor()
# # #   cursor.execute('CREATE DATABASE IF NOT EXISTS friend_db')
# # #   cursor.close()
# # #   conn.close()

# # #   # 2. Connect to friend_db and create tables
# # #   conn = pymysql.connect(**DB_CONFIG)
# # #   cursor = conn.cursor()

# # #   cursor.execute("""
# # #         CREATE TABLE IF NOT EXISTS users (
# # #             user_id INT AUTO_INCREMENT PRIMARY KEY,
# # #             username VARCHAR(50) NOT NULL,
# # #             email VARCHAR(100) UNIQUE NOT NULL
# # #         )
# # #     """)

# # #   cursor.execute("""
# # #         CREATE TABLE IF NOT EXISTS friendships (
# # #             user_id INT,
# # #             friend_id INT,
# # #             status ENUM('pending', 'accepted') DEFAULT 'accepted',
# # #             PRIMARY KEY (user_id, friend_id),
# # #             FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
# # #             FOREIGN KEY (friend_id) REFERENCES users(user_id) ON DELETE CASCADE
# # #         )
# # #     """)

# # #   cursor.execute("""
# # #         CREATE TABLE IF NOT EXISTS user_interests (
# # #             user_id INT,
# # #             interest VARCHAR(50),
# # #             PRIMARY KEY (user_id, interest),
# # #             FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
# # #         )
# # #     """)

# # #   # 3. Insert Dummy Seed Data (Testing data)
# # #   users_data = [
# # #       ('Alice', 'alice@test.com'),
# # #       ('Bob', 'bob@test.com'),
# # #       ('Charlie', 'charlie@test.com'),
# # #       ('Diana', 'diana@test.com'),
# # #       ('Evan', 'evan@test.com'),
# # #   ]

# # #   cursor.execute('SELECT COUNT(*) as count FROM users')
# # #   if cursor.fetchone()['count'] == 0:
# # #     for name, email in users_data:
# # #       cursor.execute(
# # #           'INSERT INTO users (username, email) VALUES (%s, %s)', (name, email)
# # #       )

# # #     # Seed Friendships (Graph Edges)
# # #     # Alice (1) is friends with Bob (2) and Charlie (3)
# # #     # Bob (2) is friends with Diana (4)
# # #     friendships_data = [(1, 2), (1, 3), (2, 4)]
# # #     for u, f in friendships_data:
# # #       cursor.execute(
# # #           'INSERT INTO friendships (user_id, friend_id, status) VALUES (%s, %s,'
# # #           " 'accepted')",
# # #           (u, f),
# # #       )
# # #       # Make graph undirected
# # #       cursor.execute(
# # #           'INSERT INTO friendships (user_id, friend_id, status) VALUES (%s, %s,'
# # #           " 'accepted')",
# # #           (f, u),
# # #       )

# # #     # Seed Interests (Hashing Table data)
# # #     interests_data = [
# # #         (1, 'Coding'),
# # #         (1, 'Gaming'),
# # #         (2, 'Coding'),
# # #         (3, 'Music'),
# # #         (4, 'Gaming'),
# # #         (5, 'Gaming'),
# # #         (5, 'Music'),
# # #     ]
# # #     for u, interest in interests_data:
# # #       cursor.execute(
# # #           'INSERT IGNORE INTO user_interests (user_id, interest) VALUES (%s,'
# # #           ' %s)',
# # #           (u, interest),
# # #       )

# # #     conn.commit()
# # #     print('Database initialized and seeded with test data successfully!')
# # #   else:
# # #     print('Database already contains data. Skipping seed.')

# # #   cursor.close()
# # #   conn.close()


# # # if __name__ == '__main__':
# # #   setup_database()
# # from collections import defaultdict, deque
# # from flask import Flask, jsonify, render_template, request
# # from flask_cors import CORS
# # import pymysql

# # app = Flask(__name__)
# # CORS(app)

# # # Database Configuration
# # DB_CONFIG = {
# #     'host': 'localhost',
# #     'user': 'root',
# #     'password': 'H@rsh1577',  # Update if your local MySQL has a password
# #     'database': 'friend_db',
# #     'cursorclass': pymysql.cursors.DictCursor,
# # }


# # def get_db():
# #   return pymysql.connect(**DB_CONFIG)


# # # --- MATHEMATICAL RECOMMENDATION ENGINE ---
# # def compute_mathematical_recommendations(target_user_id, cursor):
# #   adj_list = defaultdict(set)
# #   interest_table = defaultdict(set)

# #   # 1. Load Adjacency List (Graph Edges) from MySQL
# #   cursor.execute(
# #       "SELECT user_id, friend_id FROM friendships WHERE status = 'accepted'"
# #   )
# #   for row in cursor.fetchall():
# #     adj_list[row['user_id']].add(row['friend_id'])
# #     adj_list[row['friend_id']].add(row['user_id'])

# #   # 2. Load Interests into Hash Table from MySQL
# #   cursor.execute('SELECT user_id, interest FROM user_interests')
# #   for row in cursor.fetchall():
# #     interest_table[row['interest']].add(row['user_id'])

# #   target_friends = adj_list[target_user_id]
# #   scores = {}

# #   # Find Candidate Users via BFS (Friends of Friends up to 2 hops)
# #   candidates = set()
# #   visited = {target_user_id}.union(target_friends)
# #   queue = deque([(target_user_id, 0)])

# #   while queue:
# #     curr, depth = queue.popleft()
# #     if depth < 2:
# #       for neighbor in adj_list[curr]:
# #         if neighbor not in visited:
# #           if curr in target_friends and neighbor != target_user_id:
# #             candidates.add(neighbor)
# #           visited.add(neighbor)

# #   # Bridge for Cold Start: Add users sharing at least one interest tag
# #   cursor.execute(
# #       'SELECT interest FROM user_interests WHERE user_id = %s',
# #       (target_user_id,),
# #   )
# #   target_interests = {r['interest'] for r in cursor.fetchall()}

# #   for interest in target_interests:
# #     for candidate in interest_table[interest]:
# #       if candidate != target_user_id and candidate not in target_friends:
# #         candidates.add(candidate)

# #   # 3. Compute Mathematical Scores (Common Neighbors + Jaccard Coefficients)
# #   for candidate_id in candidates:
# #     candidate_friends = adj_list[candidate_id]

# #     # Metric 1: Common Neighbors Count
# #     common = target_friends.intersection(candidate_friends)
# #     common_count = len(common)

# #     # Metric 2: Network Jaccard Coefficient
# #     union = target_friends.union(candidate_friends)
# #     jaccard_score = len(common) / len(union) if len(union) > 0 else 0.0

# #     # Metric 3: Interest Similarity (Jaccard Index on Tags)
# #     cursor.execute(
# #         'SELECT interest FROM user_interests WHERE user_id = %s',
# #         (candidate_id,),
# #     )
# #     candidate_interests = {r['interest'] for r in cursor.fetchall()}

# #     shared_interests = target_interests.intersection(candidate_interests)
# #     interest_union = target_interests.union(candidate_interests)
# #     interest_score = (
# #         len(shared_interests) / len(interest_union)
# #         if len(interest_union) > 0
# #         else 0.0
# #     )

# #     # Weighted Scoring Equation
# #     final_score = (
# #         (jaccard_score * 4.0)
# #         + (float(common_count) * 2.0)
# #         + (interest_score * 1.5)
# #     )
# #     scores[candidate_id] = final_score

# #   # Rank Candidates Descending by Total Score
# #   ranked_candidates = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[
# #       :5
# #   ]

# #   # Fallback Strategy: If no graph/interest overlaps exist, suggest newest accounts
# #   if not ranked_candidates:
# #     cursor.execute(
# #         'SELECT user_id, username FROM users WHERE user_id != %s ORDER BY'
# #         ' user_id DESC LIMIT 5',
# #         (target_user_id,),
# #     )
# #     return cursor.fetchall()

# #   # Fetch Candidate Details from MySQL
# #   format_strings = ','.join(['%s'] * len(ranked_candidates))
# #   cursor.execute(
# #       f'SELECT user_id, username FROM users WHERE user_id IN ({format_strings})',
# #       tuple(ranked_candidates),
# #   )
# #   return cursor.fetchall()


# # # --- API ROUTES ---


# # @app.route('/')
# # def index():
# #   return render_template('index.html')


# # @app.route('/api/users', methods=['GET'])
# # def get_all_users():
# #   conn = get_db()
# #   cursor = conn.cursor()
# #   cursor.execute('SELECT user_id, username FROM users')
# #   users = cursor.fetchall()
# #   conn.close()
# #   return jsonify(users)


# # @app.route('/api/register', methods=['POST'])
# # def register_user():
# #   data = request.json
# #   username = data.get('username')
# #   email = data.get('email')
# #   interests = data.get('interests', [])

# #   if not username or not email:
# #     return (
# #         jsonify({'status': 'error', 'message': 'Username and Email required'}),
# #         400,
# #     )

# #   conn = get_db()
# #   cursor = conn.cursor()

# #   try:
# #     # Insert new user
# #     cursor.execute(
# #         'INSERT INTO users (username, email) VALUES (%s, %s)', (username, email)
# #     )
# #     new_user_id = cursor.lastrowid

# #     # Insert user interests
# #     for interest in interests:
# #       cursor.execute(
# #           'INSERT INTO user_interests (user_id, interest) VALUES (%s, %s)',
# #           (new_user_id, interest.strip()),
# #       )

# #     conn.commit()
# #     conn.close()

# #     return jsonify({
# #         'status': 'success',
# #         'message': 'Account created successfully!',
# #         'user_id': new_user_id,
# #         'username': username,
# #     })

# #   except Exception as e:
# #     conn.rollback()
# #     conn.close()
# #     return jsonify({'status': 'error', 'message': str(e)}), 500


# # @app.route('/api/recommendations/<int:user_id>', methods=['GET'])
# # def get_recommendations(user_id):
# #   try:
# #     conn = get_db()
# #     cursor = conn.cursor()
# #     recommendations = compute_mathematical_recommendations(user_id, cursor)
# #     conn.close()
# #     return jsonify({'status': 'success', 'recommendations': recommendations})
# #   except Exception as e:
# #     return jsonify({'status': 'error', 'message': str(e)}), 500


# # if __name__ == '__main__':
# #   app.run(debug=True, port=5000)
# from flask import Flask, render_template, request, jsonify
# from flask_cors import CORS
# import pymysql

# app = Flask(__name__)
# CORS(app)

# # MySQL Database Configuration
# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'H@rsh1577',  # Update with your actual MySQL password if you have one
#     'database': 'friend_db',
#     'cursorclass': pymysql.cursors.DictCursor
# }

# def get_db():
#     return pymysql.connect(**DB_CONFIG)

# @app.route('/')
# def index():
#     return render_template('index.html')

# # 1. API to Register a New User & Save Interests
# @app.route('/api/register', methods=['POST'])
# def register_user():
#     data = request.get_json()
#     username = data.get('username')
#     email = data.get('email')
#     interests = data.get('interests', [])

#     try:
#         conn = get_db()
#         with conn.cursor() as cursor:
#             # Insert user
#             cursor.execute("INSERT INTO users (username, email) VALUES (%s, %s)", (username, email))
#             user_id = cursor.lastrowid

#             # Insert interests
#             for interest in interests:
#                 cursor.execute("INSERT INTO user_interests (user_id, interest) VALUES (%s, %s)", (user_id, interest))
            
#             conn.commit()
#         conn.close()
        
#         return jsonify({
#             'status': 'success',
#             'user_id': user_id,
#             'username': username,
#             'message': 'Account created successfully!'
#         })
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 400

# # 2. API to Get All Users for the Dropdown Selector
# @app.route('/api/users', methods=['GET'])
# def get_all_users():
#     try:
#         conn = get_db()
#         with conn.cursor() as cursor:
#             cursor.execute("SELECT id AS user_id, username, email FROM users")
#             users = cursor.fetchall()
#         conn.close()
#         return jsonify(users)
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 400

# # 3. API to Fetch Recommendations based on Common Interests
# @app.route('/api/recommendations/<int:user_id>', methods=['GET'])
# def get_recommendations(user_id):
#     try:
#         conn = get_db()
#         with conn.cursor() as cursor:
#             # Find users who share at least one common interest and are not the current user
#             query = """
#                 SELECT DISTINCT u.id AS user_id, u.username 
#                 FROM users u
#                 JOIN user_interests ui ON u.id = ui.user_id
#                 WHERE ui.interest IN (
#                     SELECT interest FROM user_interests WHERE user_id = %s
#                 )
#                 AND u.id != %s
#                 AND u.id NOT IN (
#                     SELECT user_id2 FROM friendships WHERE user_id1 = %s
#                     UNION
#                     SELECT user_id1 FROM friendships WHERE user_id2 = %s
#                 )
#             """
#             cursor.execute(query, (user_id, user_id, user_id, user_id))
#             recommendations = cursor.fetchall()
#         conn.close()

#         return jsonify({
#             'status': 'success',
#             'recommendations': recommendations
#         })
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 400

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)
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