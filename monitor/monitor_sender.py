import requests
import json
import subprocess
import argparse

# Function to get free memory in MB
def get_free_memory():
    result = subprocess.run(['free', '-m'], stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8').split('\n')
    available_memory = int(lines[1].split()[6])
    free_memory = int(lines[1].split()[3])
    return available_memory, free_memory

# Function to check if a process is running
def is_process_running(process_name):
    result = subprocess.run(['pgrep', '-f', process_name], stdout=subprocess.PIPE)
    return result.returncode == 0

# Parse command-line arguments
parser = argparse.ArgumentParser(description='Send system data to a specified endpoint.')
parser.add_argument('rack_id', type=str, help='The rack ID to be used in the URL')
args = parser.parse_args()

# Get memory values
available_memory, free_memory = get_free_memory()

# Check if the processes are running
ps_firebaseremoteadmin = "OK" if is_process_running("firebaseremoteadmin.py") else "NO"
ps_smartbox = "OK" if is_process_running("smartbox.py") else "NO"
ps_controller_handler = "OK" if is_process_running("controller_handler.py") else "NO"
ps_firebase_main = "OK" if is_process_running("firebase_main.py") else "NO"

# Prepare the data to be sent
data = {
    "available_memory": available_memory,
    "free_memory": free_memory,
    "ps_firebaseremoteadmin": ps_firebaseremoteadmin,
    "ps_smartbox": ps_smartbox,
    "ps_controller_handler": ps_controller_handler,
    "ps_firebase_main": ps_firebase_main
}

# Send the data to the endpoint
url = f"http://report.mehter.hu:81/api/data/{args.rack_id}"
headers = {'Content-Type': 'application/json'}
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response
print(response.status_code)
print(response.json())