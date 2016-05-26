pip install -r requirements-dev.txt

# South is dependeny of django-nicedit, incompatible with django-1.8 remove it.
pip uninstall -y south

export DJANGO_SETTINGS_MODULE='spoken.settings_dev'
python manage.py runserver
