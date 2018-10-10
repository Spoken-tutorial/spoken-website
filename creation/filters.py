# Third Party Stuff
import django_filters

# Spoken Tutorial Stuff
from creation.models import TutorialResource


class CreationStatisticsFilter(django_filters.FilterSet):

    publish_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss', 'language', 'tutorial_detail__level', 'publish_at']
