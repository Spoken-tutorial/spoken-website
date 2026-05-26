from __future__ import unicode_literals

from django import forms
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import FormView

from events.views import is_resource_person

from .models import TrainingEvents
from .services import build_swayam_csv_response, resolve_moodle_quiz_id


YES_NO_CHOICES = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]

COURSE_TYPE_CHOICES = [
    ('Free', 'Free'),
    ('Paid', 'Paid'),
]


class SwayamParticipantExportForm(forms.Form):
    event = forms.ModelChoiceField(
        queryset=TrainingEvents.objects.none(),
        empty_label='---------',
        label='SWAYAM Event',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    swayam_course_id = forms.CharField(
        label='Course ID in SWAYAM Plus',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    swayam_plus_redirect_referal_id = forms.CharField(
        label='SWAYAM Plus Redirect Referal ID',
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    course_name = forms.CharField(
        label='Course Name',
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    ncrf_aligned_course = forms.ChoiceField(
        label='NCrF aligned course?',
        choices=YES_NO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    course_type = forms.ChoiceField(
        label='Type of course',
        choices=COURSE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    course_completion_status = forms.ChoiceField(
        label='Course Completion Status',
        choices=YES_NO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    course_completion_date = forms.DateField(
        label='Course Completion Date',
        input_formats=['%Y-%m-%d', '%d/%m/%Y'],
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    participation_certificate_status = forms.ChoiceField(
        label='Participation Certificate Status',
        choices=YES_NO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    assessment_certificate_status = forms.ChoiceField(
        label='Assessment Certificate Status',
        choices=YES_NO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super(SwayamParticipantExportForm, self).__init__(*args, **kwargs)
        self.fields['event'].queryset = (
            TrainingEvents.objects.filter(is_swayam=True)
            .select_related('course')
            .prefetch_related('course__foss')
            .order_by('-event_start_date', 'event_name')
        )


class DownloadSwayamParticipantDataView(FormView):
    template_name = 'training/swayam_participant_data.html'
    form_class = SwayamParticipantExportForm

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not is_resource_person(request.user):
            raise PermissionDenied()
        return super(DownloadSwayamParticipantDataView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DownloadSwayamParticipantDataView, self).get_context_data(**kwargs)
        context['page_title'] = 'Download Swayam Participant Data'
        return context

    def form_valid(self, form):
        event = form.cleaned_data['event']
        quiz_id = resolve_moodle_quiz_id(event)
        if not quiz_id:
            form.add_error('event', 'No Moodle quiz mapping found for the selected event.')
            return self.form_invalid(form)

        metadata = {
            'swayam_course_id': form.cleaned_data['swayam_course_id'],
            'swayam_plus_redirect_referal_id': form.cleaned_data['swayam_plus_redirect_referal_id'],
            'course_name': form.cleaned_data['course_name'],
            'ncrf_aligned_course': form.cleaned_data['ncrf_aligned_course'],
            'course_type': form.cleaned_data['course_type'],
            'course_completion_status': form.cleaned_data['course_completion_status'],
            'course_completion_date': form.cleaned_data['course_completion_date'],
            'participation_certificate_status': form.cleaned_data['participation_certificate_status'],
            'assessment_certificate_status': form.cleaned_data['assessment_certificate_status'],
        }

        response, _quiz_id = build_swayam_csv_response(event, metadata)
        return response