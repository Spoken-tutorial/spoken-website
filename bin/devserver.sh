#!/bin/bash
set -e
echo ">> Making sure latest requirements are installed..."
pip install -r requirements-dev.txt > /dev/null

if [ ! -f config.py ]; then
    echo ">> config.py not found. Copying config.sample.py -> config.py"
    cp config.sample.py config.py
fi

echo ">> Set django to use development settings."
export DJANGO_SETTINGS_MODULE='spoken.settings_dev'
python manage.py runserver
