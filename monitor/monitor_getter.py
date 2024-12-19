from flask import Flask, request, jsonify
import sqlite3
import datetime
import os

app = Flask(__name__)
#app.config['APPLICATION_ROOT'] = '/api'
db_path = os.path.join(os.path.dirname(__file__), 'monitor_data.db')

# Initialize the database
def init_db():
    conn = sqlite3.connect(db_path)
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
    conn = sqlite3.connect(db_path)
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


@app.route('/api/data', methods=['GET'])
def get_data():
    rack_id = request.args.get('rack_id')
    key = request.args.get('key')

    if not rack_id or not key:
        return jsonify({"error": "Missing rack_id or key"}), 400

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    five_minutes_ago = (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat()

    cursor.execute('''
        SELECT value FROM records
        WHERE rack_id = ? AND key = ? AND timestamp >= ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (rack_id, key, five_minutes_ago))

    result = cursor.fetchone()
    conn.close()

    if result:
        return jsonify({"value": result[0]}), 200
    else:
        return jsonify({"value": "NO"}), 200

@app.route('/api/process_status', methods=['GET'])
def get_process_status():
    rack_id = request.args.get('rack_id')
    if not rack_id:
        return jsonify({"error": "Missing rack_id"}), 400

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    five_minutes_ago = (datetime.datetime.now() - datetime.timedelta(minutes=5)).isoformat()

    cursor.execute('''
        SELECT key, value FROM records
        WHERE rack_id = ? AND key LIKE 'ps_%' AND timestamp >= ?
        ORDER BY timestamp DESC
    ''', (rack_id, five_minutes_ago))

    results = cursor.fetchall()
    conn.close()

    process_status = {key: value for key, value in results}

    return jsonify(process_status), 200

#if __name__ == '__main__':
#    init_db()
#    app.run(debug=True)
