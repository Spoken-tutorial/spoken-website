from builtins import str
from builtins import object
from django import forms
from django.contrib.auth.models import User
from .helpers import is_user_paid
from events.models import *
from training.models import *
from .validators import validate_csv_file

class CreateTrainingEventForm(forms.ModelForm):
    foss = forms.ModelChoiceField(empty_label='---------', queryset=FossCategory.objects.filter(show_on_homepage=1))
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
    phone = forms.RegexField(regex=r'^\+?1?\d{8,15}$', error_messages = {'required': 'Enter valid phone number.'},)
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
        model = AcademicPaymentStatus
        exclude = ['entry_user']
    
    def clean_csv_file(self):
        data = self.cleaned_data["csv_file"]
        file_data = validate_csv_file(data)
        return file_data

class TrainingManagerPaymentForm(forms.Form):
    state = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    college = forms.ChoiceField(choices=[('0', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    status = forms.ChoiceField(choices=[('', '-- None --'), ('S', 'Successfull'), ('F', 'Failed'),('X','Undefined')], required = False)
    request_type = forms.ChoiceField(choices=[('', '-- None --'), ('I', 'Initiated at Bank'), ('R', 'Reconciled')], required = False)
    fdate = forms.DateTimeField(required = False)
    tdate = forms.DateTimeField(required = False)
    events = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    user_email = forms.EmailField(max_length = 200, required = False)
    userid = forms.IntegerField(required = False)
    def __init__(self, user,*args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]

        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]

        super(TrainingManagerPaymentForm, self).__init__(*args, **kwargs)
        

        rp_states = ResourcePerson.objects.filter(status=1,user=user)
        # load the choices
        state_list = list(State.objects.filter(id__in=rp_states.values('state')).order_by('name').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        self.fields['state'].choices = state_list

        centre_choices =[]
        centre_choices.insert(0,(0,'All Colleges'))

        event_choices = []
        event_choices.insert(0,(0,'All Events'))
        
        if args:
            if 'state' in args[0]:
                if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                    centre_qs = AcademicCenter.objects.filter(state_id=args[0]['state']).order_by('institution_name')
                    centre_choices = [(x.id, '%s, %s' % (x.institution_name, x.academic_code)) for x in centre_qs]
                    centre_choices.insert(0,(0,'All Colleges'))
                    self.fields['college'].choices = centre_choices
                    self.fields['college'].widget.attrs = {}

            if 'college' in args[0]:
                if args[0]['college'] and args[0]['college'] != '' and args[0]['college'] != 'None':
                    event_qs = TrainingEvents.objects.filter(host_college_id=args[0]['college']).order_by('event_name')
                    event_choices = [(x.id, '%s, %s' % (x.event_name, x.event_type)) for x in event_qs]
                    event_choices.insert(0,(0,'All Events'))
                    self.fields['events'].choices = event_choices
                    self.fields['events'].widget.attrs = {}




