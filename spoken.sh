#!/bin/bash

sudo apt-get install python3-dev libmysqlclient-dev
sudo pip3 install virtualenv

Virtualenv venv -p python3
source venv/bin/activate

pip3 install -r requirements-dev.txt
pip3 install -r requirements-py3.txt

sudo cp sample.config.py /spoken
cd events
cat > display.py
chmod 777 display.py
cd ..



python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000



