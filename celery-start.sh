#!/bin/bash

export DJANGO_SETTINGS_MODULE=spoken.settings
celery multi start 1 -A spoken.celery:app --concurrency=5 -Q:1 scheduled_tasks --loglevel=DEBUG
celery beat -A spoken.celery:app -l DEBUG -f celerybeat.log --detach

