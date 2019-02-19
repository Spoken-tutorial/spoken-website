# Third Party Stuff
import django_filters

# Spoken Tutorial Stuff
from cms.models import News
from events.models import State, MediaTestimonials
from creation.models import FossCategory


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

class MediaTestimonialsFossFilter(django_filters.FilterSet):
    foss = django_filters.ChoiceFilter(choices=FossCategory.objects.none())

    def __init__(self, *args, **kwargs):
        super(MediaTestimonialsFossFilter, self).__init__(*args, **kwargs)

        choices = None
        choices = list(FossCategory.objects.filter(id__in=MediaTestimonials.objects.filter().values(
            'foss_id').distinct()).order_by('foss').values_list('id', 'foss'))
        choices.insert(0, ('', '---------'),)
        self.filters['foss'].extra.update({'choices': choices})

    class Meta:
        model = MediaTestimonials
        fields = ['foss']
