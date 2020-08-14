from builtins import str
from builtins import object
from django import forms
from django.contrib.auth.models import User
from .helpers import is_user_paid
from events.models import *
from training.models import *
from .validators import validate_csv_file

class CreateTrainingEventForm(forms.ModelForm):
    event_coordinator_email = forms.CharField(required = False)
    event_coordinator_contact_no = forms.CharField(required = False)
    class Meta(object):
        model = TrainingEvents
        exclude = ['entry_user', 'training_status', 'Language_of_workshop']
    

class RegisterUser(forms.ModelForm):
    
    state = forms.ModelChoiceField(
            widget = forms.Select(attrs = {'class' : 'ac-state'}),
            queryset = State.objects.order_by('name'),
            empty_label = "--- Select State ---", 
            help_text = "",
            required=True,
            )
    college = forms.CharField(
        required = False,
        error_messages = {'required': 'component type is required.'},
    )
    foss_language = forms.ModelChoiceField(
        queryset = Language.objects.order_by('name'),
        required = False,
        help_text = "You can listen to the FOSS in the above Indian languages"
    )

    class Meta(object):
        model = Participant
        fields = ['name', 'email', 'state', 'gender', 'amount', 'foss_language']

    def __init__(self, *args, **kwargs):
        super(RegisterUser, self).__init__(*args, **kwargs)
        self.fields['amount'].required = False

class UploadParticipantsForm(forms.ModelForm):
    csv_file = forms.FileField(required=True)

    class Meta(object):
        model = Participant
        fields = ['registartion_type']
    
    def clean_csv_file(self):
        data = self.cleaned_data["csv_file"]
        file_data = validate_csv_file(data)
        return file_data


class UploadCollegeForm(forms.ModelForm):
    csv_file = forms.FileField(required=True)

    class Meta(object):
        model = AcademicPaymentStatusForm
        exclude = ['entry_user']
    #     widgets = {
    # 'payment_date':DateInput(),
    # 'phone':forms.NumberInput(),
    # 'amount':forms.NumberInput()
    #     }
    
    def clean_csv_file(self):
        data = self.cleaned_data["csv_file"]
        file_data = validate_csv_file(data)
        return file_data