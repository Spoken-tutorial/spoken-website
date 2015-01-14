import django_filters
from events.models import *
from django.core.exceptions import ObjectDoesNotExist

class AcademicCenterFilter(django_filters.FilterSet):
    state = django_filters.ChoiceFilter(choices=State.objects.none())
    resource_center = django_filters.ChoiceFilter(choices=[('', '---------'), (1, 'Resource Centers Only')])
    institution_name = django_filters.CharSearchFilter()
    def __init__(self, *args, **kwargs):
        user = None
        if 'user' in kwargs:
            user = kwargs['user']
            kwargs.pop('user')
            
        super(AcademicCenterFilter, self).__init__(*args, **kwargs)
        choices = None
        if user:
            choices = list(State.objects.filter(resourceperson__user_id=user, resourceperson__status=1).values_list('id', 'name').order_by('name'))
        else:
            choices = list(State.objects.exclude(name = 'Uncategorised').values_list('id', 'name').order_by('name'))
        choices.insert(0, ('', '---------'),)
        self.filters['state'].extra.update({'choices' : choices})
    class Meta:
        model = AcademicCenter
        fields = ['state', 'institution_type', 'institute_category']

class OrganiserFilter(django_filters.FilterSet):
    academic__state = django_filters.ChoiceFilter(choices=State.objects.none())
    academic__institution_name = django_filters.CharSearchFilter()
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        kwargs.pop('user')
        super(OrganiserFilter, self).__init__(*args, **kwargs)
        choices = list(State.objects.filter(resourceperson__user_id=user, resourceperson__status=1).values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['academic__state'].extra.update({'choices' : choices})
    class Meta:
        model = Organiser
        fields = ['academic__state', 'academic__institution_type', 'academic__institute_category']

class InvigilatorFilter(django_filters.FilterSet):
    academic__state = django_filters.ChoiceFilter(choices=State.objects.none())
    academic__institution_name = django_filters.CharSearchFilter()
    def __init__(self, *args, **kwargs):
        user = kwargs['user']
        kwargs.pop('user')
        super(InvigilatorFilter, self).__init__(*args, **kwargs)
        choices = list(State.objects.filter(resourceperson__user_id=user, resourceperson__status=1).values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['academic__state'].extra.update({'choices' : choices})
    class Meta:
        model = Invigilator
        fields = ['academic__state', 'academic__institution_type', 'academic__institute_category']

class TrainingFilter(django_filters.FilterSet):
    academic__state = django_filters.ChoiceFilter(choices=State.objects.none())
    foss = django_filters.ChoiceFilter(choices= [('', '---------')] + list(FossAvailableForWorkshop.objects.filter(status=1).order_by('foss__foss').values_list('foss__id', 'foss__foss').distinct()))
    language = django_filters.ChoiceFilter(choices= [('', '---------')] + list(FossAvailableForWorkshop.objects.values_list('language__id', 'language__name').distinct()))
    training_type = django_filters.ChoiceFilter(choices= [('', '---------'), (0, 'Training'), (1, 'Workshop'), (2, 'Live Workshop'), (3, 'Pilot Workshop')])
    academic__institution_type = django_filters.ChoiceFilter(choices= [('', '---------')] + list(InstituteType.objects.values_list('id', 'name').distinct()))
    academic__city = django_filters.ChoiceFilter(choices=State.objects.none())
    tdate = django_filters.DateRangeCompareFilter()
    academic__institution_name = django_filters.CharSearchFilter()
    def __init__(self, *args, **kwargs):
        user=None
        if 'user' in kwargs:
            user = kwargs['user']
            kwargs.pop('user')
        
        state = None
        if 'state' in kwargs:
            state = kwargs['state']
            kwargs.pop('state')
        super(TrainingFilter, self).__init__(*args, **kwargs)
        if args and args[0] and 'academic__state' in args[0] and args[0]['academic__state']:
            try:
                state = State.objects.get(pk = args[0]['academic__state'])
            except ObjectDoesNotExist:
                pass
        choices = None
        if user:
            choices = list(State.objects.filter(resourceperson__user_id=user, resourceperson__status=1).values_list('id', 'name'))
        else:
            choices = list(State.objects.exclude(name='Uncategorised').order_by('name').values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['academic__state'].extra.update({'choices' : choices})
        
        choices = None
        if state:
            choices = list(City.objects.filter(state=state).order_by('name').values_list('id', 'name')) + [('189', 'Uncategorised')]
        else:
            choices = list(City.objects.none())
        choices.insert(0, ('', '---------'),)
        self.filters['academic__city'].extra.update({'choices' : choices})
        
    class Meta:
        model = Training
        fields = ['academic__state', 'foss']

class TestFilter(django_filters.FilterSet):
    academic__state = django_filters.ChoiceFilter(choices=State.objects.none())
    foss = django_filters.ChoiceFilter(choices= [('', '---------')] + list(FossAvailableForTest.objects.filter(status=1).order_by('foss__foss').values_list('foss__id', 'foss__foss').distinct()))
    test_category = django_filters.ChoiceFilter(choices= [('', '---------'), (1, 'Training'), (2, 'Workshop'), (3, 'Others'), (3, 'Pilot Workshop')])
    academic__institution_type = django_filters.ChoiceFilter(choices= [('', '---------')] + list(InstituteType.objects.values_list('id', 'name').distinct()))
    academic__city = django_filters.ChoiceFilter(choices=State.objects.none())
    tdate = django_filters.DateRangeCompareFilter()
    academic__institution_name = django_filters.CharSearchFilter()
    def __init__(self, *args, **kwargs):
        user=None
        if 'user' in kwargs:
            user = kwargs['user']
            kwargs.pop('user')
        
        state = None
        if 'state' in kwargs:
            state = kwargs['state']
            kwargs.pop('state')
        super(TestFilter, self).__init__(*args, **kwargs)
        if args and args[0] and 'academic__state' in args[0] and args[0]['academic__state']:
            try:
                state = State.objects.get(pk = args[0]['academic__state'])
            except ObjectDoesNotExist:
                pass
        choices = None
        if user:
            choices = list(State.objects.filter(resourceperson__user_id=user, resourceperson__status=1).values_list('id', 'name'))
        else:
            choices = list(State.objects.exclude(name='Uncategorised').order_by('name').values_list('id', 'name'))
        choices.insert(0, ('', '---------'),)
        self.filters['academic__state'].extra.update({'choices' : choices})
        
        choices = None
        if state:
            choices = list(City.objects.filter(state=state).order_by('name').values_list('id', 'name')) + [('189', 'Uncategorised')]
        else:
            choices = list(City.objects.none())
        choices.insert(0, ('', '---------'),)
        self.filters['academic__city'].extra.update({'choices' : choices})
        
    class Meta:
        model = Test
        fields = ['academic__state', 'foss']
