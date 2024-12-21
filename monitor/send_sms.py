import requests
import os
import time
import datetime
from monitor_dashboard import rack_info

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
    flag_file = 'sms_sent.flag'
    if os.path.exists(flag_file):
        return False  # Do not send SMS if flag file exists

    sms_url = "https://api.bipkampany.hu/sendsms"
    headers = {
        'Authorization': 'AccessKey ddc6a6ad2962963d40eaf51e3b9c5e70',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {
        'message': message,
        'number': '36208861084',
        'key': 'ddc6a6ad2962963d40eaf51e3b9c5e70'
    }
    response = requests.post(sms_url, data=payload, headers=headers)
    print(response.status_code)
    print(response.text)
    if response.status_code == 200:
        with open(flag_file, 'w') as f:
            f.write('SMS sent')
        return True
    return False

# Fetch process status for all rack IDs and send SMS if needed
def check_and_notify():
    for rack_id, info in rack_info.items():
        status = get_process_status(rack_id, info['tzadd'])
        for key in info['keys']:
            if key.startswith('ps_') and (status.get(key) == "NO" or status.get(key) == "" or status.get(key) == None):
                rack_prefix = info['name'].split(':')[0]
                message = f"Alert: {rack_prefix} ({rack_id}) - {key} is {status.get(key)}"
                print(message)
                send_sms(message)

# Main loop to periodically check the process status
def main():
    while True:
        check_and_notify()
        time.sleep(5 * 60)  # Wait for 5 minutes before checking again

if __name__ == "__main__":
    main()