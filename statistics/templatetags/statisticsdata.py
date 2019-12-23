# Standard Library
import datetime as dt

# Third Party Stuff
from django import template

# Spoken Tutorial Stuff
from events.models import TrainingRequest

register = template.Library()


def get_valid_statistics(academic_center, model_name):
    if model_name == 'training':
        return TrainingRequest.objects.filter(
            training_planner__academic=academic_center,
            participants__gt=0,
            sem_start_date__lte=dt.datetime.now()
        ).order_by('-sem_start_date')
    return academic_center.filter(participant_count__gt=0, status=4).order_by('-tdate')


def get_valid_statistics_count(academic_center, model_name):
    collection = get_valid_statistics(academic_center, model_name)
    return collection.count()

def get_gender_ratio(collection):
	print("########################")
	print(collection.object_list)
	print("########################")
	return collection





register.filter('get_valid_statistics', get_valid_statistics)
register.filter('get_valid_statistics_count', get_valid_statistics_count)
register.filter('get_gender_ratio', get_gender_ratio)
