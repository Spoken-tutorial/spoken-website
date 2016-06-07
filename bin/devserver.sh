#!/bin/bash
set -e
echo ">> Making sure latest requirements are installed..."
pip install -r requirements-dev.txt > /dev/null

echo ">> Set django to use development settings."
export DJANGO_SETTINGS_MODULE='spoken.settings_dev'
python manage.py runserver
