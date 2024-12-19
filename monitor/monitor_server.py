from flask import Flask, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            timestamp TEXT,
            rack_id TEXT,
            key TEXT,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Insert data into the database
def insert_data(rack_id, data):
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    for key, value in data.items():
        cursor.execute('''
            INSERT INTO records (timestamp, rack_id, key, value)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, rack_id, key, value))
    conn.commit()
    conn.close()

@app.route('/api/data/<rack_id>', methods=['POST'])
def receive_data(rack_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    insert_data(rack_id, data)
    return jsonify({"message": "Data inserted successfully"}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)