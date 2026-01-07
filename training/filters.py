import django_filters
from .models import Company
from training.models import Participant
from creation.models import FossCategory
from events.models import State, AcademicCenter
from training.models import TrainingEvents, Participant


class CompanyFilter(django_filters.FilterSet):
    class Meta:
        model = Company
        fields = ['name', 'state', 'company_type']


