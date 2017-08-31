import django_filters
from creation.models import TutorialResource, PublishTutorialLog


class CreationStatisticsFilter(django_filters.FilterSet):

    publishtutoriallog__created = django_filters.DateRangeCompareFilter()

    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss','language', 'tutorial_detail__level']
