from django.contrib.auth.models import User
from donate.models import *
from django import forms
from events.models import State	

class PayeeForm(forms.ModelForm):
    state = forms.ModelChoiceField(
            widget = forms.Select(attrs = {'class' : 'ac-state'}),
            queryset = State.objects.order_by('name'),
            empty_label = "--- None ---", 
            help_text = "",
            required=False,
            )   

    class Meta(object):
        model = Payee
        exclude = ['created','updated']

