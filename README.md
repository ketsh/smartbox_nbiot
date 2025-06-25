

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



# Installing new packages in venv

cd /var/www/smartbox_nbiot
source venv/bin/activate
pip3 install -r requirements.txt
cp -R venv /var/www/smartbox_nbiot/monitor

# Creaing new apache2 config
cp /etc/apache2/sites-available/smartbox_nbiot_monitor.conf /etc/apache2/sites-available/smartbox_nbiot_dashboard.conf
nano /etc/apache2/sites-available/smartbox_nbiot_dashboard.conf
--set up (new ports, patsh ,...)
a2ensite smartbox_nbiot_dashboard.conf

Adding ports
nano /etc/apache2/ports.conf
--add Listen 8050

ufw allow 8050
ufw reload

reload apache2
systemctl reload apache2
systemctl restart apache2

Setting up permissions
chmod -R 755 /var/www/smartbox_nbiot
chown -R www-data:www-data /var/www/smartbox_nbiot

Check config
apachectl configtest

# Git pull new changes OLD

cd /var/www/smartbox_nbiot
git pull 
systemctl restart apache2

# Starting monitoring
IN case of restarting the machine, you need to manually start the streamlit dashboard
source /var/www/smartbox_nbiot/monitor/start_streamlit_app.sh &


# Git pull new changes - streamlit

cd /var/www/smartbox_nbiot
git pull 
ps -ef | grep streamlit
kill -9 <PID>
source /var/www/smartbox_nbiot/monitor/start_streamlit_app.sh &

# Deploying to PROD
Deploy Infrastructure through Remote admin
Check if it works:
python3 /home/konyvlada/smartbox_infra/monitor_py/monitor_sender.py LCFEL7NLIqFX4Cw6GQit

crontab -l
*/5 * * * * python3 /home/konyvlada/smartbox_infra/monitor_py/monitor_sender.py LCFEL7NLIqFX4Cw6GQit &

# Checking DB

cd /var/www/smartbox_nbiot/monitor
sqlite3 monitor_data.db
select * from records where rack_id = '3o3ZcwEuKJ7aM0i5g7RY' order by timestamp desc LIMIT 20;

## Getting memory consumption
select * from records where rack_id = '3o3ZcwEuKJ7aM0i5g7RY' and timestamp between '2025-03-02T16:00' and '2025-03-02T22:00' and key in ( 'available_memory', 'ps_smartbox') order by timestamp desc;

## Adding new rack
Add it to monitor_config.py

If you have added a new rack id, then you need to restart the the apache again
systemctl restart apache2