#!/bin/bash
export WORKSPACE='var/lib/jenkins/workspace/venv/bin'

if [ ! -d "venv" ]; then
        virtualenv venv
fi
. venv/bin/activate





#sudo apt-get install python3-dev libmysqlclient-dev

pwd
pip3 install -r requirements-dev.txt
pip3 install -r requirements-py3.txt



#cd Spoken tutorial script creation 

cp sample.config.py spoken/config.py
cd spoken

chown jenkins:jenkins config.py
cd ..
cd events

cat > display.py
chmod 777 display.py
pwd
cd ..
pwd

python3 manage.py makemigrations
python3 manage.py migrate
#nohup python3 manage.py runserver 10.129.132.169:8000 &
#python3 manage.py runserver 0.0.0.0:8000

