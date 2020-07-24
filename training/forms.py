from builtins import str
from builtins import object
from django import forms
from django.contrib.auth.models import User
from .helpers import is_user_paid
from events.models import *
from training.models import *

class CreateTrainingEventForm(forms.ModelForm):

   class Meta(object):
    model = TrainingEvents
    exclude = ['entry_user']
    

class RegisterUser(forms.ModelForm):
    
    state = forms.ModelChoiceField(
            widget = forms.Select(attrs = {'class' : 'ac-state'}),
            queryset = State.objects.order_by('name'),
            empty_label = "--- Select State ---", 
            help_text = "",
            required=False,
            )
    college = forms.CharField(
        required = False,
        error_messages = {'required': 'component type is required.'},
    ) 

    class Meta(object):
        model = Participant
        fields = ['name', 'email', 'state', 'gender', 'amount']

    def __init__(self, *args, **kwargs):
        super(RegisterUser, self).__init__(*args, **kwargs)
        self.fields['amount'].required = False

