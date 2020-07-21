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
    

    class Meta(object):
        model = Participant
        fields = ['name', 'email', 'state', 'gender', 'amount', 'event', 'college']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        print("user is -->",user)
        super(RegisterUser, self).__init__(*args, **kwargs)	
        if user:
                if user.is_authenticated:
                        self.fields['email'].initial = user.email
                        self.fields['email'].widget.attrs['readonly'] = True
                        self.fields['name'].initial = user.get_full_name()
        if 'user' in kwargs:
            print("kw user :",kwargs["user"])
            self.user = kwargs["user"]
            del kwargs["user"]
            user_paid_info = is_user_paid(self.user)
            if user_paid_info[0]:
                 self.fields['college'].initial = user_paid_info[1]
     
