import django_filters
from events.models import *

class AcademicCenterFilter(django_filters.FilterSet):
    
    #state = django_filters.ChoiceFilter(choices = list(State.objects.all().values_list('id', 'name')))
    def __init__(self, *args, **kwargs):
        self._user = kwargs.pop('user')
        super(AcademicCenterFilter, self).__init__(*args, **kwargs)
        #print self._user
        #print self.filters['state']
    
    class Meta:
        model = AcademicCenter
        fields = ['state', 'institution_type', 'institute_category']
