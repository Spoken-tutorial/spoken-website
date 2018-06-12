# Third Party Stuff
import django_filters

# Spoken Tutorial Stuff
from creation.models import TutorialResource, RoleRequest
from django import forms

class CreationStatisticsFilter(django_filters.FilterSet):

    publish_at = django_filters.DateRangeCompareFilter()
    #script_user_id = django_filters.ChoiceFilter( name='user__username')


    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss', 'language', 'tutorial_detail__level', 'publish_at','script_user']

	