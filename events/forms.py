
from django import forms

#import Model form
from django.forms import ModelForm

#import events models
from events.models import *
from django.contrib.auth.models import User, Group

class RpForm(forms.ModelForm):
	user = forms.ModelChoiceField(queryset = User.objects.filter(groups__name='Resource Person'))
	state = forms.ModelChoiceField(queryset = State.objects.all())
	status = forms.BooleanField(required=False)
	class Meta:
		model = ResourcePerson
		exclude = ['assigned_by']

class AcademicForm(forms.ModelForm):
	state = forms.ModelChoiceField(label='State', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-state'}), queryset = State.objects.order_by('name'), empty_label = "--- None ---", help_text = "", error_messages = {'required':'State field required.'})
	
	university = forms.ModelChoiceField(label='University', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-university'}), queryset = University.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'University field required.'})
	
	institution_type = forms.ModelChoiceField(label='Institute Type', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-institution_type'}), queryset = InstituteType.objects.all(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'Institute Type field required.'})
	
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
		self.fields["state"].queryset = State.objects.filter(resourceperson__user_id=user).filter(resourceperson__status=1)
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
		model = AcademicCenter
		exclude = ['user', 'academic_code']

class OrganiserForm(forms.Form):
	state = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
	district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'district field is required.'})
	college = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
	
	def __init__(self, *args, **kwargs):
		initial = ''
		if 'instance' in kwargs:
			initial = kwargs["instance"]
			del kwargs["instance"]
			
		super(OrganiserForm, self).__init__(*args, **kwargs)
		#load the choices
		state_list = list(State.objects.exclude(name='uncategorized').values_list('id', 'name'))
		state_list.insert(0, ('', '-- None --'))
		self.fields['state'].choices = state_list
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
					choices = list(AcademicCenter.objects.filter(district_id = args[0]['district']).values_list('id', 'institution_name'))
					choices.insert(0, ('', '-- None --'))
					self.fields['college'].choices = choices
					self.fields['college'].widget.attrs = {}
					#self.fields['college'].initial = args[0]['collages']
		if initial:
			self.fields['state'].initial = initial.academic.state_id
			self.fields['district'].choices = District.objects.filter(state_id =initial.academic.state_id).values_list('id', 'name')
			self.fields['college'].choices = AcademicCenter.objects.filter(district_id =initial.academic.district_id).values_list('id', 'institution_name')
			#initial data
			self.fields['district'].initial = initial.academic.district_id
			self.fields['college'].initial = initial.academic_id

class InvigilatorForm(forms.Form):
	state = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
	district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'district field is required.'})
	college = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
	def __init__(self, *args, **kwargs):
		initial = ''
		if 'instance' in kwargs:
			initial = kwargs["instance"]
			del kwargs["instance"]
			
		super(InvigilatorForm, self).__init__(*args, **kwargs)
		#load the choices
		state_list = list(State.objects.exclude(name='uncategorized').values_list('id', 'name'))
		state_list.insert(0, ('', '-- None --'))
		self.fields['state'].choices = state_list
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
					choices = list(AcademicCenter.objects.filter(district_id = args[0]['district']).values_list('id', 'institution_name'))
					choices.insert(0, ('', '-- None --'))
					self.fields['college'].choices = choices
					self.fields['college'].widget.attrs = {}
					#self.fields['college'].initial = args[0]['collages']
		if initial:
			self.fields['state'].initial = initial.academic.state_id
			self.fields['district'].choices = District.objects.filter(state_id =initial.academic.state_id).values_list('id', 'name')
			self.fields['college'].choices = AcademicCenter.objects.filter(district_id =initial.academic.district_id).values_list('id', 'institution_name')
			#initial data
			self.fields['district'].initial = initial.academic.district_id
			self.fields['college'].initial = initial.academic_id

class DepartmentForm(forms.ModelForm):
	class Meta:
		model = Department

class WorkshopForm(forms.Form):
	#state_list = list(State.objects.exclude(name='uncategorized').values_list('id', 'name'))
	#state_list.insert(0, ('', '-- None --'))
	#state = forms.ChoiceField(choices = state_list, widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
	district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'district field is required.'})
	academic = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
	department = forms.MultipleChoiceField(choices = [('', '-- None --'),], widget=forms.SelectMultiple(attrs = {}), required = True, error_messages = {'required':'Department Name field is required.'})
	wdate = forms.DateTimeField(required = True, error_messages = {'required':'Date field is required.'})
	foss = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'Foss field is required.'})
	language = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'Language field is required.'})
	skype = forms.ChoiceField(widget=forms.RadioSelect, choices=[(0, 'No'),(1, 'Yes')], required = True)
	def __init__(self, *args, **kwargs):
		user = ''
		if 'user' in kwargs:
			user = kwargs["user"]
			del kwargs["user"]
		instance = ''
		if 'instance' in kwargs:
			instance = kwargs["instance"]
			del kwargs["instance"]
		super(WorkshopForm, self).__init__(*args, **kwargs)
		#choices data 
		self.fields['department'].choices = Department.objects.exclude(name='uncategorized').values_list('id', 'name')

		foss_list = list(Foss_Category.objects.all().values_list('id', 'foss'))
		foss_list.insert(0, ('', '-- None --'))
		lang_list = list(Language.objects.all().values_list('id', 'name'))
		lang_list.insert(0, ('', '-- None --'))
		self.fields['foss'].choices = foss_list
		self.fields['language'].choices = lang_list
		if user:
			#self.fields['state'].initial = user.organiser.academic.state.id
			self.fields['district'].choices = District.objects.filter(state =user.organiser.academic.state).values_list('id', 'name')
			self.fields['district'].initial = user.organiser.academic.district.id
			if args and 'district' in args[0]:
					choices = AcademicCenter.objects.filter(district =args[0]['district']).values_list('id', 'institution_name')
			else:
				choices = AcademicCenter.objects.filter(district =user.organiser.academic.district).values_list('id', 'institution_name')
				
			self.fields['academic'].choices = choices
			#self.fields['academic'].initial = user.organiser.academic.id
		if instance:
			#self.fields['state'].initial = user.organiser.academic.state.id
			self.fields['district'].choices = District.objects.filter(state =instance.academic.state).values_list('id', 'name')
			self.fields['district'].initial = instance.academic.district.id
			self.fields['academic'].choices = AcademicCenter.objects.filter(district =instance.academic.district).values_list('id', 'institution_name')
			self.fields['academic'].initial = instance.academic_id
			self.fields['department'].initial = instance.department.all().values_list('id', flat=True)
			self.fields['wdate'].initial = str(instance.wdate) + " " + str(instance.wtime)[0:5]
			self.fields['foss'].initial = instance.foss_id
			self.fields['language'].initial = instance.language_id
			self.fields['skype'].initial = instance.status

class WorkshopPermissionForm(forms.Form):
	permission_choices = list(PermissionType.objects.all().values_list('id', 'name'))
	permission_choices.insert(0, ('', '-- None --'))
	permissiontype = forms.ChoiceField(choices = permission_choices, widget=forms.Select(attrs = {}), required = True)
	
	user_list = list(User.objects.filter(groups__name='Workshop Permission').values_list('id', 'username'))
	user_list.insert(0, ('', '-- None --'))
	user = forms.ChoiceField(choices = user_list, widget=forms.Select(attrs = {}), required = True)
	
	state_list = list(State.objects.exclude(name='uncategorized').values_list('id', 'name'))
	state_list.insert(0, ('', '-- None --'))
	state = forms.ChoiceField(choices = state_list, widget=forms.Select(attrs = {}), required = True)
	
	district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False, error_messages = {'required':'district field is required.'})
	
	university =  forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False)
	
	institution_type = list(InstituteType.objects.order_by('name').values_list('id', 'name'))
	institution_type.insert(0, ('', '-- None --'))
	institutiontype = forms.ChoiceField(choices = institution_type, widget=forms.Select(attrs = {}), required = False)
	
	institute = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False)

	def __init__(self, *args, **kwargs):
		super(WorkshopPermissionForm, self).__init__(*args, **kwargs)
		if args:
			if 'state' in args[0] and 'district' in args[0]:
				if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
					choices = list(District.objects.filter(state_id = args[0]['state']).values_list('id', 'name'))
					choices.insert(0, ('', '-- None --'))
					self.fields['district'].choices = choices
					
			if 'state' in args[0] and 'university' in args[0]:
				if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
					choices = list(University.objects.filter(state_id = args[0]['state']).values_list('id', 'name'))
					choices.insert(0, ('', '-- None --'))
					self.fields['university'].choices = choices
					
			if 'district' in args[0] and 'institute' in args[0]:
				if args[0]['district'] and args[0]['district'] != '' and args[0]['district'] != 'None':
					choices = list(AcademicCenter.objects.filter(district_id = args[0]['district']).values_list('id', 'institution_name'))
					choices.insert(0, ('', '-- None --'))
					self.fields['institute'].choices = choices
