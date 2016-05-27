#!/bin/bash
pip install -r requirements-dev.txt

if [ ! -f config.py ]; then
    cp config.sample.py config.py
fi

echo "create database test_spoken;" | mysql -uroot
mysql -uroot test_spoken < /path/to/test_spoken.sql
