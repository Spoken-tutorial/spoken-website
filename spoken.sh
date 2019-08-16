#!/bin/bash

#export WORKSPACE=`pwd`
virtualenv spkenv -p python3
source spkenv/bin/activate

cd Spoken tutorial script creation


sudo apt-get install python3-dev libmysqlclient-dev

pwd
pip3 install -r requirements-dev.txt
pip3 install -r requirements-py3.txt



#cd Spoken tutorial script creation 

sudo cp sample.config.py spoken/config.py
cd spoken

sudo chown jenkins:jenkins config.py
cd ..
cd events

cat > display.py
chmod 777 display.py
pwd
cd ..
pwd


python3 manage.py migrate
#python3 manage.py runserver 0.0.0.0:8000



