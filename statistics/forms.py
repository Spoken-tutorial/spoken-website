from django import forms

from statistics.models import *

class LearnerForm(forms.ModelForm):
    class Meta:
        model = Learner
