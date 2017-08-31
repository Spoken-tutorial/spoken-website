import django_filters
from creation.models import TutorialResource


class CreationStatisticsFilter(django_filters.FilterSet):

    updated = django_filters.DateRangeCompareFilter()

    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss', 'updated', 'language', 'tutorial_detail__level']
