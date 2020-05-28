from django.contrib.auth.models import User
from donate.models import *

class NewDonor(forms.ModelForm):
    state = forms.ModelChoiceField(queryset=State.objects.all().defer('User').order_by('name'))
    state = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    class Meta(object):
        model = Donor
        exclude = ['created','updated']

