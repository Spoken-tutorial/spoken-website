import django_filters
from creation.models import TutorialResource


class CreationStatisticsFilter(django_filters.FilterSet):

    created = django_filters.DateRangeCompareFilter()

    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss', 'created', 'language', 'tutorial_detail__level']
