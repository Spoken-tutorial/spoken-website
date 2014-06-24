import django_filters
from events.models import *

class AcademicCenterFilter(django_filters.FilterSet):
    
    #todo: load only RP states
    #state = django_filters.ChoiceFilter(choices = list(State.objects.all().values_list('id', 'name')))
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(AcademicCenterFilter, self).__init__(*args, **kwargs)
        #print self._user
        #print self.filters['state']
    
    class Meta:
        model = AcademicCenter
        fields = ['state', 'institution_type', 'institute_category']

class OrganiserFilter(django_filters.FilterSet):
    class Meta:
        model = Organiser
        fields = ['academic__state', 'academic__institution_type', 'academic__institute_category']

class InvigilatorFilter(django_filters.FilterSet):
    class Meta:
        model = Invigilator
        fields = ['academic__state', 'academic__institution_type', 'academic__institute_category']

class WorkshopFilter(django_filters.FilterSet):
    workshop_type = django_filters.ChoiceFilter(choices = (('', '---------'), (0,'Workshop'), (1, 'Pilot Workshop'), (2, 'Live Workshop'),))
    class Meta:
        model = Workshop
        fields = ['academic__state', 'foss', 'workshop_type']

class TrainingFilter(django_filters.FilterSet):
    class Meta:
        model = Training
        fields = ['academic__state', 'foss']

class TestFilter(django_filters.FilterSet):
    class Meta:
        model = Test
        fields = ['academic__state', 'foss', 'test_category']
