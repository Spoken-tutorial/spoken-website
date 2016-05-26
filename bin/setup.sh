#!/bin/bash
pip install -r requirements-dev.txt

echo "create database test_spoken;" | mysql -uroot
mysql -uroot test_spoken < /path/to/test_spoken.sql
