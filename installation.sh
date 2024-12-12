#!/bin/bash



# Enable exit on error
set -e



# APT installations
sudo apt-get install -y python3-pip
sudo apt-get install -y python3.8-venv
python3 -m venv venv

source venv/bin/activate


pip3 install wheel
pip3 install -r requirements.txt

deactivate
