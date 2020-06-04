from django.contrib.auth.models import User
from donate.models import *
from django import forms
from events.models import State	


class PaymentForm(forms.ModelForm):

    state = forms.ModelChoiceField(
            widget = forms.Select(attrs = {'class' : 'ac-state'}),
            queryset = State.objects.order_by('name'),
            empty_label = "--- Select State ---", 
            help_text = "",
            required=False,
            ) 

    class Meta:
        model = Payment
        fields = ['name', 'email', 'country', 'state', 'gender', 'amount', 'foss', 'language']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Please enter your name'})
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Your register email id.'})
        self.fields['country'].widget.attrs.update({'class': 'form-control'})
        self.fields['country'].initial = 'India'
        self.fields['state'].widget.attrs.update({'class': 'form-control'})
        self.fields['gender'].widget.attrs.update({'class': 'form-control'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control'})
        self.fields['foss'].widget = forms.HiddenInput()
        self.fields['language'].widget = forms.HiddenInput()
        