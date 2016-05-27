#!/bin/bash

pip install -r requirements-dev.txt

if [ ! -f config.py ]; then
    cp config.sample.py config.py
fi

export DJANGO_SETTINGS_MODULE='spoken.settings_dev'
python manage.py runserver
