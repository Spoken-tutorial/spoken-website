# Third Party Stuff
import django_filters

# Spoken Tutorial Stuff
from creation.models import TutorialResource, ContributorRating


class CreationStatisticsFilter(django_filters.FilterSet):

    publish_at = django_filters.DateRangeCompareFilter()

    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss', 'language', 'tutorial_detail__level', 'publish_at', 'script_user', 'video_user' ,'submissiondate']


class ContributorRatingFilter(django_filters.FilterSet):

    class Meta:
        model = ContributorRating
        fields = ['language', 'user']
