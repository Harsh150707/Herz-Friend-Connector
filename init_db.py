# from collections import defaultdict, deque
# from flask import Flask, jsonify, render_template, request
# from flask_cors import CORS
# import pymysql

# app = Flask(__name__)
# CORS(app)

# DB_CONFIG = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': '',
#     'database': 'friend_db',
#     'cursorclass': pymysql.cursors.DictCursor,
# }


# def get_db():
#   return pymysql.connect(**DB_CONFIG)


# def compute_mathematical_recommendations(target_user_id, cursor):
#   adj_list = defaultdict(set)
#   interest_table = defaultdict(set)

#   # 1. Load Adjacency List from MySQL
#   cursor.execute(
#       "SELECT user_id, friend_id FROM friendships WHERE status = 'accepted'"
#   )
#   for row in cursor.fetchall():
#     adj_list[row['user_id']].add(row['friend_id'])
#     adj_list[row['friend_id']].add(row['user_id'])

#   # 2. Load Interests into Hash Table
#   cursor.execute('SELECT user_id, interest FROM user_interests')
#   for row in cursor.fetchall():
#     interest_table[row['interest']].add(row['user_id'])

#   target_friends = adj_list[target_user_id]
#   scores = {}

#   # Find candidates via BFS (Friends of Friends up to 2 hops)
#   candidates = set()
#   visited = {target_user_id}.union(target_friends)
#   queue = deque([(target_user_id, 0)])

#   while queue:
#     curr, depth = queue.popleft()
#     if depth < 2:
#       for neighbor in adj_list[curr]:
#         if neighbor not in visited:
#           if curr in target_friends and neighbor != target_user_id:
#             candidates.add(neighbor)
#           visited.add(neighbor)

#   # Bridge for cold-start: users sharing at least one interest
#   cursor.execute(
#       'SELECT interest FROM user_interests WHERE user_id = %s',
#       (target_user_id,),
#   )
#   target_interests = {r['interest'] for r in cursor.fetchall()}

#   for interest in target_interests:
#     for candidate in interest_table[interest]:
#       if candidate != target_user_id and candidate not in target_friends:
#         candidates.add(candidate)

#   # 3. Compute Mathematical Scores (Common Neighbors + Jaccard Coefficient + Interest Overlap)
#   for candidate_id in candidates:
#     candidate_friends = adj_list[candidate_id]

#     # Metric 1: Common Neighbors Count
#     common = target_friends.intersection(candidate_friends)
#     common_count = len(common)

#     # Metric 2: Jaccard Coefficient on Network Topology
#     union = target_friends.union(candidate_friends)
#     jaccard_score = len(common) / len(union) if len(union) > 0 else 0.0

#     # Metric 3: Interest Similarity Jaccard Index
#     cursor.execute(
#         'SELECT interest FROM user_interests WHERE user_id = %s',
#         (candidate_id,),
#     )
#     candidate_interests = {r['interest'] for r in cursor.fetchall()}

#     shared_interests = target_interests.intersection(candidate_interests)
#     interest_union = target_interests.union(candidate_interests)
#     interest_score = (
#         len(shared_interests) / len(interest_union)
#         if len(interest_union) > 0
#         else 0.0
#     )

#     # Weighted Final Formula
#     final_score = (
#         (jaccard_score * 4.0)
#         + (float(common_count) * 2.0)
#         + (interest_score * 1.5)
#     )
#     scores[candidate_id] = final_score

#   # Rank candidates descending
#   ranked_candidates = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[
#       :5
#   ]

#   if not ranked_candidates:
#     cursor.execute(
#         'SELECT user_id, username FROM users WHERE user_id != %s LIMIT 5',
#         (target_user_id,),
#     )
#     return cursor.fetchall()

#   format_strings = ",".join(['%s'] * len(ranked_candidates))
#   cursor.execute(
#       f'SELECT user_id, username FROM users WHERE user_id IN ({format_strings})',
#       tuple(ranked_candidates),
#   )
#   return cursor.fetchall()


# # --- API ROUTES ---


# @app.route('/')
# def index():
#   return render_template('index.html')


# @app.route('/api/users', methods=['GET'])
# def get_all_users():
#   conn = get_db()
#   cursor = conn.cursor()
#   cursor.execute('SELECT user_id, username FROM users')
#   users = cursor.fetchall()
#   conn.close()
#   return jsonify(users)


# @app.route('/api/recommendations/<int:user_id>', methods=['GET'])
# def get_recommendations(user_id):
#   try:
#     conn = get_db()
#     cursor = conn.cursor()
#     recommendations = compute_mathematical_recommendations(user_id, cursor)
#     conn.close()
#     return jsonify({'status': 'success', 'recommendations': recommendations})
#   except Exception as e:
#     return jsonify({'status': 'error', 'message': str(e)}), 500


# if __name__ == '__main__':
#   app.run(debug=True, port=5000)
from collections import defaultdict, deque
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'H@rsh1577',
    'database': 'friend_db',
    'cursorclass': pymysql.cursors.DictCursor,
}


def get_db():
  return pymysql.connect(**DB_CONFIG)


def compute_mathematical_recommendations(target_user_id, cursor):
  adj_list = defaultdict(set)
  interest_table = defaultdict(set)

  # 1. Load Adjacency List from MySQL
  cursor.execute(
      "SELECT user_id, friend_id FROM friendships WHERE status = 'accepted'"
  )
  for row in cursor.fetchall():
    adj_list[row['user_id']].add(row['friend_id'])
    adj_list[row['friend_id']].add(row['user_id'])

  # 2. Load Interests into Hash Table
  cursor.execute('SELECT user_id, interest FROM user_interests')
  for row in cursor.fetchall():
    interest_table[row['interest']].add(row['user_id'])

  target_friends = adj_list[target_user_id]
  scores = {}

  # Find candidates via BFS (Friends of Friends up to 2 hops)
  candidates = set()
  visited = {target_user_id}.union(target_friends)
  queue = deque([(target_user_id, 0)])

  while queue:
    curr, depth = queue.popleft()
    if depth < 2:
      for neighbor in adj_list[curr]:
        if neighbor not in visited:
          if curr in target_friends and neighbor != target_user_id:
            candidates.add(neighbor)
          visited.add(neighbor)

  # Bridge for cold-start: users sharing at least one interest
  cursor.execute(
      'SELECT interest FROM user_interests WHERE user_id = %s',
      (target_user_id,),
  )
  target_interests = {r['interest'] for r in cursor.fetchall()}

  for interest in target_interests:
    for candidate in interest_table[interest]:
      if candidate != target_user_id and candidate not in target_friends:
        candidates.add(candidate)

  # 3. Compute Mathematical Scores (Common Neighbors + Jaccard Coefficient + Interest Overlap)
  for candidate_id in candidates:
    candidate_friends = adj_list[candidate_id]

    # Metric 1: Common Neighbors Count
    common = target_friends.intersection(candidate_friends)
    common_count = len(common)

    # Metric 2: Jaccard Coefficient on Network Topology
    union = target_friends.union(candidate_friends)
    jaccard_score = len(common) / len(union) if len(union) > 0 else 0.0

    # Metric 3: Interest Similarity Jaccard Index
    cursor.execute(
        'SELECT interest FROM user_interests WHERE user_id = %s',
        (candidate_id,),
    )
    candidate_interests = {r['interest'] for r in cursor.fetchall()}

    shared_interests = target_interests.intersection(candidate_interests)
    interest_union = target_interests.union(candidate_interests)
    interest_score = (
        len(shared_interests) / len(interest_union)
        if len(interest_union) > 0
        else 0.0
    )

    # Weighted Final Formula
    final_score = (
        (jaccard_score * 4.0)
        + (float(common_count) * 2.0)
        + (interest_score * 1.5)
    )
    scores[candidate_id] = final_score

  # Rank candidates descending
  ranked_candidates = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[
      :5
  ]

  if not ranked_candidates:
    cursor.execute(
        'SELECT user_id, username FROM users WHERE user_id != %s LIMIT 5',
        (target_user_id,),
    )
    return cursor.fetchall()

  format_strings = ','.join(['%s'] * len(ranked_candidates))
  cursor.execute(
      f'SELECT user_id, username FROM users WHERE user_id IN ({format_strings})',
      tuple(ranked_candidates),
  )
  return cursor.fetchall()


# --- API ROUTES ---


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/api/users', methods=['GET'])
def get_all_users():
  conn = get_db()
  cursor = conn.cursor()
  cursor.execute('SELECT user_id, username FROM users')
  users = cursor.fetchall()
  conn.close()
  return jsonify(users)


# --- REGISTRATION ROUTE (Added) ---
@app.route('/api/register', methods=['POST'])
def register_user():
  data = request.json
  username = data.get('username')
  email = data.get('email')
  interests = data.get('interests', [])

  if not username or not email:
    return (
        jsonify({'status': 'error', 'message': 'Username and Email required'}),
        400,
    )

  conn = get_db()
  cursor = conn.cursor()

  try:
    cursor.execute(
        'INSERT INTO users (username, email) VALUES (%s, %s)', (username, email)
    )
    new_user_id = cursor.lastrowid

    for interest in interests:
      cursor.execute(
          'INSERT INTO user_interests (user_id, interest) VALUES (%s, %s)',
          (new_user_id, interest.strip()),
      )

    conn.commit()
    conn.close()

    return jsonify({
        'status': 'success',
        'message': 'Account created successfully!',
        'user_id': new_user_id,
        'username': username,
    })

  except Exception as e:
    conn.rollback()
    conn.close()
    return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
  try:
    conn = get_db()
    cursor = conn.cursor()
    recommendations = compute_mathematical_recommendations(user_id, cursor)
    conn.close()
    return jsonify({'status': 'success', 'recommendations': recommendations})
  except Exception as e:
    return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
  app.run(debug=True, port=5000)