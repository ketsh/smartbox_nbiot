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

# Check if the process is running
process_status = "OK" if is_process_running("firebaseremoteadmin.py") else "NO"

# Prepare the data to be sent
data = {
    "available_memory": available_memory,
    "free_memory": free_memory,
    "process_status": process_status
}

# Send the data to the endpoint
url = "http://report.mehter.hu:81/api/data/999"
headers = {'Content-Type': 'application/json'}
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response
print(response.status_code)
print(response.json())