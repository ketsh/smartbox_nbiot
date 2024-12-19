import sys
import os

# Add the application's directory to the Python path
sys.path.insert(0, '/var/www/smartbox_nbiot/monitor')

# Activate the virtual environment
#activate_this = '/var/www/smartbox_nbiot/monitor/venv/bin/activate_this.py'
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))

# Import the Dash app
from monitor_dashboard import server as application
