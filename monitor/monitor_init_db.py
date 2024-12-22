import sqlite3
import os

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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sms_status (
            timestamp TEXT,
            sms_sent INTEGER
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()