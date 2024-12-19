import requests
import json
import subprocess

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
url = "http://report.mehter.hu:81/api/data/999"
headers = {'Content-Type': 'application/json'}
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response
print(response.status_code)
print(response.json())