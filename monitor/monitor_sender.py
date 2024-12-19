import requests
import json
import subprocess

# Function to get free memory in MB
def get_free_memory():
    result = subprocess.run(['free', '-m'], stdout=subprocess.PIPE)
    lines = result.stdout.decode('utf-8').split('\n')
    available_memory = int(lines[1].split()[6])
    return available_memory

# Prepare the data to be sent
data = {
    "available_memory": get_free_memory()
}

# Send the data to the endpoint
url = "http://report.mehter.hu:81/api/data/999"
headers = {'Content-Type': 'application/json'}
response = requests.post(url, headers=headers, data=json.dumps(data))

# Print the response
print(response.status_code)
print(response.json())