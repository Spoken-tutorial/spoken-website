import django_filters
from events.models import *

class AcademicCenterFilter(django_filters.FilterSet):
    state = django_filters.ChoiceFilter(choices=State.objects.none())
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        kwargs.pop('user')
        super(AcademicCenterFilter, self).__init__(*args, **kwargs)
        choices = list(State.objects.filter(resourceperson__user_id=user).values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['state'].extra.update({'choices' : choices})
    class Meta:
        model = AcademicCenter
        fields = ['state', 'institution_type', 'institute_category']

class OrganiserFilter(django_filters.FilterSet):
    academic__state = django_filters.ChoiceFilter(choices=State.objects.none())
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        kwargs.pop('user')
        super(OrganiserFilter, self).__init__(*args, **kwargs)
        choices = list(State.objects.filter(resourceperson__user_id=user).values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['academic__state'].extra.update({'choices' : choices})
    class Meta:
        model = Organiser
        fields = ['academic__state', 'academic__institution_type', 'academic__institute_category']

class InvigilatorFilter(django_filters.FilterSet):
    academic__state = django_filters.ChoiceFilter(choices=State.objects.none())
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        kwargs.pop('user')
        super(InvigilatorFilter, self).__init__(*args, **kwargs)
        choices = list(State.objects.filter(resourceperson__user_id=user).values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['academic__state'].extra.update({'choices' : choices})
    class Meta:
        model = Invigilator
        fields = ['academic__state', 'academic__institution_type', 'academic__institute_category']

class TrainingFilter(django_filters.FilterSet):
    academic__state = django_filters.ChoiceFilter(choices=State.objects.none())
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        kwargs.pop('user')
        super(TrainingFilter, self).__init__(*args, **kwargs)
        choices = list(State.objects.filter(resourceperson__user_id=user).values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['academic__state'].extra.update({'choices' : choices})
    class Meta:
        model = Training
        fields = ['academic__state', 'foss']

class TestFilter(django_filters.FilterSet):
    academic__state = django_filters.ChoiceFilter(choices=State.objects.none())
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        kwargs.pop('user')
        super(TestFilter, self).__init__(*args, **kwargs)
        choices = list(State.objects.filter(resourceperson__user_id=user).values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['academic__state'].extra.update({'choices' : choices})
    class Meta:
        model = Test
        fields = ['academic__state', 'foss', 'test_category']
