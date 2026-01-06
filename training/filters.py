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


class ViewEventFilter(django_filters.FilterSet):

    state = django_filters.ModelChoiceFilter(
        field_name='event__state',
        queryset=State.objects.all()
    )

    foss = django_filters.ModelChoiceFilter(
        field_name='event__foss',
        queryset=FossCategory.objects.all()
    )

    host_college = django_filters.ModelChoiceFilter(
        field_name='event__host_college',
        queryset=AcademicCenter.objects.all()
    )

    event_type = django_filters.ChoiceFilter(
        field_name='event__event_type',
        choices=TrainingEvents._meta.get_field('event_type').choices
    )

    event_start_date = django_filters.DateFromToRangeFilter(
        field_name='event__event_start_date'
    )

    event_end_date = django_filters.DateFromToRangeFilter(
        field_name='event__event_end_date'
    )

    class Meta:
        model = Participant
        fields = []   # 🔥 THIS IS CRITICAL — NOTHING ELSE
