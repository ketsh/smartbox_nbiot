

#Running on server
./venv/bin/activate
python3 ./udp_server_sender/send_backend_api.py

Running on port 5000

#Testing it
curl -X POST "http://80.211.194.137:5000/open_door?boardID=0&doorID=11"


#Set up apache2

sudo nano /etc/apache2/sites-available/smartbox_nbiot.conf
a2ensite smartbox_nbiot.conf


sudo apt install libapache2-mod-wsgi-py3

sudo a2enmod wsgi

sudo systemctl restart apache2

We ran it on /var/www
