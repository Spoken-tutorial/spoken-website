import django_filters
from creation.models import TutorialResource, FossSuperCategory


class CreationStatisticsFilter(django_filters.FilterSet):

    tutorial_detail__updated = django_filters.DateRangeCompareFilter()

    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss__category', 'tutorial_detail__foss', 'tutorial_detail__updated', 'language', 'tutorial_detail__level']
