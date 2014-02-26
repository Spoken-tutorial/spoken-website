
from django import forms

#import Model form
from django.forms import ModelForm

#import events models
from events.models import *
from django.contrib.auth.models import User, Group

class StateForm(forms.ModelForm):
	latitude = forms.CharField(required=False)
	longtitude = forms.CharField(required=False)
	img_map_area = forms.CharField(widget=forms.Textarea, required=False)
	class Meta:
		model = State
		fields = ['code', 'name', 'latitude', 'longtitude', 'img_map_area']
	def clean_latitude(self):
		if self.cleaned_data['latitude'] < 10:
			raise forms.ValidationError("exceding")
		# Always return the cleaned data
		return self.cleaned_data['latitude']

class RpForm(forms.ModelForm):
	user = forms.ModelChoiceField(queryset = User.objects.filter(groups__name='Resource Person'))
	state = forms.ModelChoiceField(queryset = State.objects.all())
	status = forms.BooleanField(required=False)
	class Meta:
		model = Resource_person
		exclude = ['assigned_by']

class AcademicForm(forms.ModelForm):
	state = forms.ModelChoiceField(label='State', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-state'}), queryset = State.objects.order_by('name'), empty_label = "--- None ---", help_text = "", error_messages = {'required':'State field required.'})
	
	university = forms.ModelChoiceField(label='University', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-university'}), queryset = University.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'University field required.'})
	
	institution_type = forms.ModelChoiceField(label='Institute Type', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-institution_type'}), queryset = Institute_type.objects.order_by('name'), empty_label = "--- None ---", help_text = "", error_messages = {'required':'Institute Type field required.'})
	
	district = forms.ModelChoiceField(label='Dist', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-district'}), queryset = District.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'Institute Type field required.'})
	
	city = forms.ModelChoiceField(label='City', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-city'}), queryset = City.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'City Type field required.'})
	
	location = forms.ModelChoiceField(label='Location', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-location'}), queryset = Location.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'City Type field required.'})
	
	contact_person = forms.CharField(widget = forms.Textarea(attrs = {'rows' : '5'}), required = False)
	remarks = forms.CharField(widget = forms.Textarea(attrs = {'rows' : '5'}), required = False)
	rating = forms.ChoiceField(choices = (('1', 'Rating 1'), ('2', 'Rating 2'), ('3', 'Rating 3'), ('4', 'Rating 4'), ('5', 'Rating 5')))
	def __init__(self, user, *args, **kwargs):
		initial = ''
		if 'instance' in kwargs:
			initial = kwargs["instance"]
			
		if 'user' in kwargs:
			user = kwargs["user"]
			del kwargs["user"]
			
		super(AcademicForm, self).__init__(*args, **kwargs)
		#initial
		self.fields["state"].queryset = State.objects.filter(resource_person__user_id=user).filter(resource_person__status=1)
		#prevent ajax loaded data
		if args:
			if 'district' in args[0]:
				if args[0]['district'] and args[0]['district'] != '' and args[0]['district'] != 'None':
					self.fields["location"].queryset = Location.objects.filter(district__id=args[0]['district'])
					
			if 'state' in args[0]:
				if args[0]['state'] != '' and args[0]['state'] != 'None':
					self.fields["university"].queryset = University.objects.filter(state__id=args[0]['state'])
					self.fields["district"].queryset = District.objects.filter(state__id=args[0]['state'])
					self.fields["city"].queryset = City.objects.filter(state__id=args[0]['state'])
		#for edit
		if initial:
			self.fields["location"].queryset = Location.objects.filter(district__id=initial.district_id)
			self.fields["university"].queryset = University.objects.filter(state__id=initial.state_id)
			self.fields["district"].queryset = District.objects.filter(state__id=initial.state_id)
			self.fields["city"].queryset = City.objects.filter(state__id=initial.state_id)
			
	class Meta:
		model = Academic_center
		exclude = ['user', 'academic_code']

class OrganiserForm(forms.Form):
	state_list = list(State.objects.exclude(name='uncategorized').values_list('id', 'name'))
	state_list.insert(0, ('', '-- None --'))
	state = forms.ChoiceField(choices = state_list, widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
	district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'district field is required.'})
	college = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
	
	def __init__(self, *args, **kwargs):
		initial = ''
		if 'instance' in kwargs:
			initial = kwargs["instance"]
			del kwargs["instance"]
			
		super(OrganiserForm, self).__init__(*args, **kwargs)
		if args:
			if 'state' in args[0]:
				if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
					choices = list(District.objects.filter(state_id = args[0]['state']).values_list('id', 'name'))
					choices.insert(0, ('', '-- None --'))
					self.fields['district'].choices = choices
					self.fields['district'].widget.attrs = {}
					self.fields['district'].initial = args[0]['district']
			if 'district' in args[0]:
				if args[0]['district'] and args[0]['district'] != '' and args[0]['district'] != 'None':
					choices = list(Academic_center.objects.filter(district_id = args[0]['district']).values_list('id', 'institution_name'))
					choices.insert(0, ('', '-- None --'))
					self.fields['college'].choices = choices
					self.fields['college'].widget.attrs = {}
					#self.fields['college'].initial = args[0]['collages']
		if initial:
			self.fields['state'].initial = initial.academic.state_id
			self.fields['district'].choices = District.objects.filter(state_id =initial.academic.state_id).values_list('id', 'name')
			self.fields['college'].choices = Academic_center.objects.filter(district_id =initial.academic.district_id).values_list('id', 'institution_name')
			#initial data
			self.fields['district'].initial = initial.academic.district_id
			self.fields['college'].initial = initial.academic_id
			
