# Third Party Stuff
from django import forms


class FeedBackForm(forms.Form):
    name = forms.CharField(max_length=30)
    email = forms.EmailField()
