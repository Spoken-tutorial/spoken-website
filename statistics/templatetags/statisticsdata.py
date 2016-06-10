# Standard Library
from datetime import datetime

# Third Party Stuff
from django import template

# Spoken Tutorial Stuff
from events.models import *

register = template.Library()


def get_valid_statistics(academic_center, model_name):
    if model_name == 'training':
        return TrainingRequest.objects.filter(
            training_planner__academic=academic_center,
            participants__gt=0,
            sem_start_date__lte=datetime.now()
        ).order_by('-sem_start_date')
    return academic_center.filter(participant_count__gt=0, status=4).order_by('-tdate')


def get_valid_statistics_count(academic_center, model_name):
    collection = get_valid_statistics(academic_center, model_name)
    return collection.count()

register.filter('get_valid_statistics', get_valid_statistics)
register.filter('get_valid_statistics_count', get_valid_statistics_count)
