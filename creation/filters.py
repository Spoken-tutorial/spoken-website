# Third Party Stuff
from builtins import object
import django_filters

# Spoken Tutorial Stuff
from creation.models import TutorialResource, ContributorRating


class CreationStatisticsFilter(django_filters.FilterSet):

    publish_at = django_filters.DateFromToRangeFilter()

    class Meta(object):
        model = TutorialResource
        fields = ['tutorial_detail__foss', 'language', 'tutorial_detail__level', 'publish_at', 'script_user', 'video_user' ,'submissiondate']


class ContributorRatingFilter(django_filters.FilterSet):

    class Meta:
        model = ContributorRating
        fields = ['language', 'user']


class ReviewerFilter(django_filters.FilterSet):

    class Meta:
        model = TutorialResource
        fields = ['tutorial_detail__foss', 'language']
