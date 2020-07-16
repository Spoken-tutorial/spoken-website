from builtins import str
from builtins import object
from django import forms
from django.contrib.auth.models import User

from events.models import *
from training.models import *

class CreateTrainingEventForm(forms.ModelForm):

   class Meta(object):
    model = TrainingEvents
    exclude = ['entry_user'] 