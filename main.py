from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__, static_folder="public", static_url_path="")
CORS(app)

DB_FILE = "game_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_scores (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            math_high_score INTEGER DEFAULT 0,
            puzzle_high_score INTEGER DEFAULT 0,
            uno_wins INTEGER DEFAULT 0,
            memory_best_time INTEGER DEFAULT 9999
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return app.send_static_file('index.html')

@app.route('/api/save-score', methods=['POST'])
def save_score():
    data = request.json
    user_id = data.get('user_id')
    username = data.get('username', 'Player')
    game_type = data.get('game_type')
    score = data.get('score')

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM user_scores WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO user_scores (user_id, username) VALUES (?, ?)", (user_id, username))

    if game_type == 'math':
        cursor.execute("UPDATE user_scores SET math_high_score = MAX(math_high_score, ?) WHERE user_id = ?", (score, user_id))
    elif game_type == 'puzzle':
        cursor.execute("UPDATE user_scores SET puzzle_high_score = MAX(puzzle_high_score, ?) WHERE user_id = ?", (score, user_id))
    elif game_type == 'uno':
        cursor.execute("UPDATE user_scores SET uno_wins = uno_wins + 1 WHERE user_id = ?", (user_id,))
    elif game_type == 'memory':
        cursor.execute("UPDATE user_scores SET memory_best_time = MIN(memory_best_time, ?) WHERE user_id = ?", (score, user_id))

    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Score Saved!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
