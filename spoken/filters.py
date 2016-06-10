# Third Party Stuff
import django_filters

# Spoken Tutorial Stuff
from cms.models import *
from creation.models import *


class NewsStateFilter(django_filters.FilterSet):
    state = django_filters.ChoiceFilter(choices=State.objects.none())

    def __init__(self, *args, **kwargs):
        news_type_slug = None
        if 'news_type_slug' in kwargs:
            news_type_slug = kwargs['news_type_slug']
            kwargs.pop('news_type_slug')

        super(NewsStateFilter, self).__init__(*args, **kwargs)

        choices = None
        choices = list(State.objects.filter(id__in=News.objects.filter(news_type__slug=news_type_slug).values(
            'state_id').distinct()).order_by('name').values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['state'].extra.update({'choices': choices})

    class Meta:
        model = News
        fields = ['state']
