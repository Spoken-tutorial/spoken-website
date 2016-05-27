pip install -r requirements-dev.txt

export DJANGO_SETTINGS_MODULE='spoken.settings_dev'
python manage.py runserver
