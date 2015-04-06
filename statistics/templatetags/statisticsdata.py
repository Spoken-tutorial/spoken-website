from django import template
from events.models import *
register = template.Library()


def get_valid_statistics(training, count=False):
    if count:
        return training.filter(participant_count__gt=0, status=4).count()
    return training.filter(participant_count__gt=0, status=4)

register.filter('get_valid_statistics', get_valid_statistics)
