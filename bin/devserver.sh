#!/bin/bash
set -e

# Bootstrap
source bin/scripts/setup-vars.sh
source bin/scripts/setup-functions.sh

check_virtualenv_is_active
check_mysql_server_is_running
install_python_requirements

echo "[django] Setting DJANGO_SETTINGS_MODULE='spoken.settings_dev'"
export DJANGO_SETTINGS_MODULE='spoken.settings_dev'

echo "[django] Starting development server"
python manage.py runserver
