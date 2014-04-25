
from django import forms

#import Model form
from django.forms import ModelForm

#import events models
from events.models import *
from django.contrib.auth.models import User, Group

class OfflineDataForm(forms.Form):
	workshop_code = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'Workshop field is required.'})
	xml_file  = forms.FileField(required=True)
	
	def __init__(self,user, *args, **kwargs):
		super(OfflineDataForm, self).__init__(*args, **kwargs)
		#load the choices
		workshop_list = list(Workshop.objects.filter(organiser_id=user.id, status = 1).values_list('id', 'workshop_code'))
		workshop_list.insert(0, ('', '-- None --'))
		self.fields['workshop_code'].choices = workshop_list

