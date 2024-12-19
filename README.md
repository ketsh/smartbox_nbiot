

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



# Deploying to PROD
Deploy Infrastructure through Remote admin
Check if it works:
python3 /home/konyvlada/smartbox_infra/monitor_py/monitor_sender.py LCFEL7NLIqFX4Cw6GQit

crontab -l
*/5 * * * * python3 /home/konyvlada/smartbox_infra/monitor_py/monitor_sender.py LCFEL7NLIqFX4Cw6GQit &