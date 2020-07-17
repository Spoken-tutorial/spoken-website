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
    """docstring for RegisterUser"""
    state = forms.ChoiceField(
        choices=[('', '-- None --'), ],
        widget=forms.Select(attrs = {}), 
        required = True,
        error_messages = {'required':'State field is required.'})
    college = forms.ChoiceField(
        choices=[('', '-- None --'), ],
        widget=forms.Select(attrs = {}),
        required = True,
        error_messages = {'required':'College Name field is required.'})

    def __init__(self, *args, **kwargs):
        # load the choices
        state_list = list(State.objects.exclude().order_by('name').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        self.fields['state'].choices = state_list

        if 'user' in kwargs:
            self.user = kwargs["user"]
            del kwargs["user"]

        ''' 
            User Paid Details
            0 - True/False
            1 - AcademicCentre
        '''
        user_paid_info = is_user_paid(self.user)
        if user_paid_info[0]:
            self.fields['college'].initial = user_paid_info[1]

        if args:
            if 'state' in args[0]:
                if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                    choices = list(AcademicCenter.objects.filter(
                        state_id = args[0]['state']).values_list('id', 'institution_name'))
                    choices.insert(0, ('', '-- None --'))
                    self.fields['college'].choices = choices
                    self.fields['college'].widget.attrs = {}    