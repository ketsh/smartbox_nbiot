import requests
import os
import time
import datetime
from monitor_config import rack_info
import random
import string
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), 'monitor_data.db')


# Function to get process status for a given rack ID
def get_process_status(rack_id, tzadd):
    url = f"http://report.mehter.hu:81/api/process_status"
    params = {'rack_id': rack_id, 'tzadd': tzadd}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {}

# Function to send SMS and create a flag file
def send_sms(message):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(*) FROM sms_status WHERE sms_sent = 1
    ''')
    result = cursor.fetchone()
    if result[0] > 0:
        conn.close()
        return False  # Do not send SMS if a record exists in the sms_status table

    response1 = sending_sms(message, '4367761649272')
    sms_status_write(response1)
    response2 = sending_sms(message, '36304628788')
    if response1.status_code != 200:
        sms_status_write(response2)

def sms_status_write(response):
    if response.status_code == 200:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO sms_status (timestamp, sms_sent)
            VALUES (?, ?)
        ''', (timestamp, 1))
        conn.commit()
        conn.close()
        return True
    return False

def sending_sms(message, number):
    sms_url = "https://api.bipkampany.hu/sendsms"
    random_hash = generate_random_hash()
    headers = {
        'Authorization': 'AccessKey ddc6a6ad2962963d40eaf51e3b9c5e70',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'message': message,
        'number': number,
        'key': 'ddc6a6ad2962963d40eaf51e3b9c5e70',
        'referenceid': random_hash,
        'type': "unicode",
        'format': "json",
        'callback': None
    }
    response = requests.post(sms_url, data=payload, headers=headers)
    print(response.status_code)
    print(response.text)
    return response


# Fetch process status for all rack IDs and send SMS if needed
def check_and_notify():
    for rack_id, info in rack_info.items():
        if rack_id not in ['bzAi1DPflIKzg75ipRF3', 'placeholder']:
            status = get_process_status(rack_id, info['tzadd'])
            for key in info['keys']:
                if key.startswith('ps_') and (status.get(key) == "NO" or status.get(key) == "" or status.get(key) == None):
                    rack_prefix = info['name'].split(':')[0]
                    message = f"Alert:{rack_prefix} {key} error"
                    print(message)
                    send_sms(message)
                    break
                if key =='memory_available_rate':
                    if int(status.get(key)) < 20:
                        rack_prefix = info['name'].split(':')[0]
                        message = f"MEMAlert:{rack_prefix} {key} error"
                        print(message)
                        send_sms(message)
                        break


def generate_random_hash():
    # Generate a random 12-character alphanumeric string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))


# Main loop to periodically check the process status
def main():
    check_and_notify()

if __name__ == "__main__":
    main()