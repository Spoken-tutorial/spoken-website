#!/bin/bash
set -e

echo ">> Install python requirements from 'requirements-dev.txt'"
pip install -r requirements-dev.txt > /dev/null

if [ ! -f config.py ]; then
    echo ">> Copying 'config.sample.py -> config.py'"
    cp config.sample.py config.py
fi

echo ">> Provide your local mysql credentials in order to import inital test database."
read -p "MySQL Username:" db_user
read -sp "MySQL Password:" db_pass
read -p "MySQL sqldump path:" db_dump

echo "create database test_spoken;" | mysql -uroot
mysql --user=$db_user --password=$db_pass test_spoken < $db_dump
