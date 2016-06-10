# Third Party Stuff
from django import forms


class MasqueradeHomeForm(forms.Form):
    username_email = forms.CharField(
        required=True,
        error_messages={'required': 'username/email is required.'},
    )
