from django.contrib.auth.models import User
from django.db.models import Q
from django import forms

class MasqueradeHomeForm(forms.Form):
    username_email = forms.CharField(
        required = True,
        error_messages = {'required': 'username/email is required.'},
    )
