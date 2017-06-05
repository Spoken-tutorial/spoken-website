import django_filters
from creation.models import TutorialResource


class CreationStatisticsFilter(django_filters.FilterSet):

    tutorial_detail__updated = django_filters.DateRangeCompareFilter()

    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss', 'tutorial_detail__created', 'language', 'tutorial_detail__level']
