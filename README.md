

Running on server
./venv/bin/activate
python3 ./udp_server_sender/send_backend_api.py

Running on port 5000

Testing it
curl -X POST "http://80.211.194.137:5000/open_door?boardID=0&doorID=11"