#!/bin/bash

export WORKSPACE=`pwd`
mkvirtualenv --python=/usr/bin/python3 testing
workon testing


sudo apt-get install python3-dev libmysqlclient-dev
pip3 install -r requirements-dev.txt
pip3 install -r requirements-py3.txt


ls -al
#cd Spoken tutorial script creation 

cp sample.config.py spoken/config.py
cd events
cat > display.py
chmod 777 display.py
cd ..
pwd
ls -al

python3 manage.py migrate
#python3 manage.py runserver 0.0.0.0:8000



