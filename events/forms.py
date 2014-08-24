
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
    
    district = forms.ModelChoiceField(label='Dist', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-district'}), queryset = District.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'Institute Type field required.'})
    
    city = forms.ModelChoiceField(label='City', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-city'}), queryset = City.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'City Type field required.'})
    
    location = forms.ModelChoiceField(label='Location', cache_choices=True, widget = forms.Select(attrs = {'class' : 'ac-location'}), queryset = Location.objects.none(), empty_label = "--- None ---", help_text = "", error_messages = {'required':'City Type field required.'}, required = False)
    
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
        self.fields["state"].queryset = State.objects.filter(resourceperson__user = user, resourceperson__status = 1)
        #prevent ajax loaded data
        if args:
            #if 'district' in args[0]:
            #    if args[0]['district'] and args[0]['district'] != '' and args[0]['district'] != 'None':
            #        self.fields["location"].queryset = Location.objects.filter(district__id=args[0]['district'])
            #        
            if 'state' in args[0]:
                if args[0]['state'] != '' and args[0]['state'] != 'None':
                    self.fields["university"].queryset = University.objects.filter(state__id=args[0]['state'])
                    self.fields["district"].queryset = District.objects.filter(state__id=args[0]['state'])
                    self.fields["city"].queryset = City.objects.filter(state__id=args[0]['state'])
        #for edit
        if initial:
            #self.fields["location"].queryset = Location.objects.filter(district__id=initial.district_id)
            self.fields["university"].queryset = University.objects.filter(state__id=initial.state_id)
            self.fields["district"].queryset = District.objects.filter(state__id=initial.state_id)
            self.fields["city"].queryset = City.objects.filter(state__id=initial.state_id)
            
    class Meta:
        model = AcademicCenter
        exclude = ['user', 'academic_code', 'institute_category']

'''
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
        state_list = list(State.objects.exclude().order_by('name').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        self.fields['state'].choices = state_list
        if args:
            if 'state' in args[0]:
                if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                    choices = list(District.objects.filter(state_id = args[0]['state']).order_by('name').values_list('id', 'name'))
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
            self.fields['district'].choices = District.objects.filter(state_id =initial.academic.state_id).order_by('name').values_list('id', 'name')
            self.fields['college'].choices = AcademicCenter.objects.filter(district_id =initial.academic.district_id).values_list('id', 'institution_name')
            #initial data
            self.fields['district'].initial = initial.academic.district_id
            self.fields['college'].initial = initial.academic_id
'''
class OrganiserForm(forms.Form):
    state = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
    college = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
    
    def __init__(self, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]
            
        super(OrganiserForm, self).__init__(*args, **kwargs)
        #load the choices
        state_list = list(State.objects.exclude().order_by('name').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        self.fields['state'].choices = state_list
        if args:
            if 'state' in args[0]:
                if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                    choices = list(AcademicCenter.objects.filter(state_id = args[0]['state']).values_list('id', 'institution_name'))
                    choices.insert(0, ('', '-- None --'))
                    self.fields['college'].choices = choices
                    self.fields['college'].widget.attrs = {}
        if initial:
            self.fields['state'].initial = initial.academic.state_id
            self.fields['college'].choices = AcademicCenter.objects.filter(district_id =initial.academic.district_id).values_list('id', 'institution_name')
            #initial data
            self.fields['college'].initial = initial.academic_id
'''
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
        state_list = list(State.objects.exclude().values_list('id', 'name'))
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
'''

class InvigilatorForm(forms.Form):
    state = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
    college = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
    def __init__(self, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]
            
        super(InvigilatorForm, self).__init__(*args, **kwargs)
        #load the choices
        state_list = list(State.objects.exclude().values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        self.fields['state'].choices = state_list
        if args:
            if 'state' in args[0]:
                if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                    choices = list(AcademicCenter.objects.filter(state_id = args[0]['state']).values_list('id', 'institution_name'))
                    choices.insert(0, ('', '-- None --'))
                    self.fields['college'].choices = choices
                    self.fields['college'].widget.attrs = {}
        if initial:
            self.fields['state'].initial = initial.academic.state_id
            self.fields['college'].choices = AcademicCenter.objects.filter(district_id =initial.academic.district_id).values_list('id', 'institution_name')
            #initial data
            self.fields['college'].initial = initial.academic_id

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department

class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        exclude = ['status', 'participant_counts', 'extra_fields', 'organiser', 'academic', 'training_code', 'trtime', 'appoved_by']
    
    def clean_course_number(self):
        super(TrainingForm, self).clean()
        if 'training_type' in self.cleaned_data:
            if self.cleaned_data['training_type'] == '0' and self.cleaned_data['course_number'] == '':
                raise forms.ValidationError("Course Number field is required.")
                
    training_type = forms.ChoiceField(widget=forms.RadioSelect, choices = [(0, 'Training'),(1, 'Workshop')], required = True)
    course_number = forms.CharField(required = False)
    tester = forms.CharField(required = False)

    department = forms.ModelMultipleChoiceField(label='Department', cache_choices=True, widget = forms.SelectMultiple(attrs = {}), queryset = Department.objects.exclude(name='Uncategorized').order_by('name'), help_text = "", error_messages = {'required':'Department field required.'})
    
    foss = forms.ModelChoiceField(label='Foss', cache_choices=True, widget = forms.Select(attrs = {}), queryset = FossCategory.objects.filter(status = 1, id__in = FossAvailableForWorkshop.objects.all().values_list('foss').distinct()).order_by('foss')
, help_text = "", error_messages = {'required':'Foss field required.'})
    
    language = forms.ModelChoiceField(label='Language', cache_choices=True, widget = forms.Select(attrs = {}), queryset = Language.objects.filter(id__in = FossAvailableForWorkshop.objects.all().values_list('language').distinct()).order_by('name'), help_text = "", error_messages = {'required':'Language field required.'})
    
    trdate = forms.DateTimeField(required = True, error_messages = {'required':'Date field is required.'})
    skype = forms.ChoiceField(widget=forms.RadioSelect, choices=[(0, 'No'),(1, 'Yes')], required = True)
    xml_file  = forms.FileField(required = True)
    def __init__(self, *args, **kwargs):
        user = ''
        tmp = 0
        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]
        instance = ''
        if 'instance' in kwargs:
            instance = kwargs["instance"]
            del kwargs["instance"]
        super(TrainingForm, self).__init__(*args, **kwargs)
        if user:
            if instance:
                self.fields['xml_file'].required = False
            from events.views import is_resource_person
            if is_resource_person(user):
                self.fields['training_type'].choices = [(0, 'Training'),(1, 'Workshop'),(2, 'Pilot Workshop'), (3, 'Live Workshop')]
        if instance:
            self.fields['training_type'].initial = instance.training_type
            self.fields['course'].initial = instance.course_id
            self.fields['foss'].initial = instance.foss
            self.fields['language'].initial = instance.language
            self.fields['trdate'].initial = str(instance.trdate) + " " + str(instance.trtime)[0:5]
            self.fields['department'].initial = instance.department.all().values_list('id', flat=True)
            self.fields['skype'].initial = instance.skype
            try:
                self.fields['course_number'].initial = instance.extra_fields.paper_name
            except Exception, e:
                #print e
                self.fields['course_number'].initial = ''
            
class TrainingPermissionForm(forms.Form):
    try:
        permission_choices = list(PermissionType.objects.all().values_list('id', 'name'))
        permission_choices.insert(0, ('', '-- None --'))
        permissiontype = forms.ChoiceField(choices = permission_choices, widget=forms.Select(attrs = {}), required = True)
        
        user_list = list(User.objects.filter(groups__name='Workshop Permission').values_list('id', 'username'))
        user_list.insert(0, ('', '-- None --'))
        user = forms.ChoiceField(choices = user_list, widget=forms.Select(attrs = {}), required = True)
        
        state_list = list(State.objects.exclude(name='Uncategorized').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        state = forms.ChoiceField(choices = state_list, widget=forms.Select(attrs = {}), required = True)
        
        district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False, error_messages = {'required':'district field is required.'})
        
        university =  forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False)
        
        institution_type = list(InstituteType.objects.order_by('name').values_list('id', 'name'))
        institution_type.insert(0, ('', '-- None --'))
        institutiontype = forms.ChoiceField(choices = institution_type, widget=forms.Select(attrs = {}), required = False)
        
        institute = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False)

        def __init__(self, *args, **kwargs):
            super(TrainingPermissionForm, self).__init__(*args, **kwargs)
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
    except:
        pass

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        exclude = ['status', 'participant_count', 'organiser', 'academic', 'test_code', 'ttime', 'training', 'workshop', 'appoved_by']
    
    def clean_workshop(self):
        super(TestForm, self).clean()
        if 'test_category' in self.cleaned_data:
            if self.cleaned_data['test_category'].id == 1 and self.cleaned_data['workshop'] == '':
                raise forms.ValidationError("Workshop field is required.")
    
    def clean_training(self):
        super(TestForm, self).clean()
        if 'test_category' in self.cleaned_data:
            if self.cleaned_data['test_category'].id == 2 and self.cleaned_data['training'] == '':
                raise forms.ValidationError("Training field is required.")
            
    tdate = forms.DateTimeField(required = True, error_messages = {'required':'Date field is required.'})
    workshop = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False, error_messages = {'required':'Workshop field is required.'})
    training = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False, error_messages = {'required':'Training field is required.'})
    foss = forms.ModelChoiceField(label='Foss', cache_choices=True, widget = forms.Select(attrs = {}), queryset = FossCategory.objects.filter(id__in = FossAvailableForTest.objects.all().values_list('foss').distinct()).order_by('foss')
, help_text = "", error_messages = {'required':'Foss field required.'})
    department = forms.ModelMultipleChoiceField(label='Department', cache_choices=True, widget = forms.SelectMultiple(attrs = {}), queryset = Department.objects.exclude(name='Uncategorized').order_by('name'), help_text = "", error_messages = {'required':'Department field required.'})
    
    def __init__(self, *args, **kwargs):
        user = ''
        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]
        instance = ''
        if 'instance' in kwargs:
            instance = kwargs["instance"]
            del kwargs["instance"]
        super(TestForm, self).__init__(*args, **kwargs)
        
        if user:
            try:
                self.fields['invigilator'].queryset = Invigilator.objects.filter(academic  = user.organiser.academic, status=1).exclude(user_id = user.id)
                wchoices = list(Training.objects.filter(academic = user.organiser.academic, status = 4, training_type__gt=0).values_list('id', 'training_code'))
                wchoices.insert(0, ('', '-- None --'))
                trchoices = list(Training.objects.filter(academic = user.organiser.academic, status = 4, training_type = 0).values_list('id', 'training_code'))
                trchoices.insert(0, ('', '-- None --'))
                self.fields['workshop'].choices = wchoices
                self.fields['training'].choices = trchoices
            except:
                pass
            
        if instance:
            self.fields['invigilator'].queryset = Invigilator.objects.filter(academic  = instance.organiser.academic, status=1).exclude(user_id = user.id)
            self.fields['invigilator'].initial = instance.invigilator
            self.fields['test_category'].initial = instance.test_category
            self.fields['foss'].initial = instance.foss
            self.fields['tdate'].initial = str(instance.tdate) + " " + str(instance.ttime)[0:5]
            self.fields['department'].initial = instance.department.all().values_list('id', flat=True)
            if instance.test_category.id == 1:
                self.fields['workshop'].initial = instance.training_id
            if instance.test_category.id == 2:
                self.fields['training'].initial = instance.training_id

class TrainingScanCopyForm(forms.Form):
    scan_copy = forms.FileField(label = 'Select a Scaned copy', required = True)
    def clean(self):
        super(TrainingScanCopyForm, self).clean()
        file_type = ['application/pdf']
        if 'scan_copy' in self.cleaned_data:
            if not component.content_type in file_type:
                raise forms.ValidationError("You have forgotten about Fred!")
        else:
            raise forms.ValidationError("You have forgotten about Fred!")

class ParticipantSearchForm(forms.Form):
    email = forms.EmailField(required = False)
    username = forms.CharField(required =  False)
    
class TrainingCompletionForm(forms.Form):
    approximate_hour = forms.ChoiceField(choices=[('', '---------'), (0, '0 - 5'), (1, '6 - 10') , (2, '11 - 15'), (3, '16 - 20'), (4, ' > 20')])
    online_test = forms.ChoiceField(choices=[('', '---------'), (0, 'Will Request'), (1, 'Will not Request'), (2, 'Already Requested')])
    is_tutorial_useful = forms.ChoiceField(widget=forms.RadioSelect, choices=[(1, 'Yes'), (0, 'No')])
    future_training = forms.ChoiceField(widget=forms.RadioSelect, choices=[(1, 'Yes'), (0, 'No')])
    recommend_to_others = forms.ChoiceField(widget=forms.RadioSelect, choices=[(1, 'Yes'), (0, 'No')])
    def __init__(self, *args, **kwargs):
        user = ''
        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]
        super(TrainingCompletionForm, self).__init__(*args, **kwargs)
#        if user:
#            if user.organiser.test_organiser.filter(status=4).count():
#                self.fields['online_test'].choices=[('', '---------'), (0, 'Will Request'), (1, 'Will not Request')]
