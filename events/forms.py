
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
        state_list = list(State.objects.exclude(name='Uncategorized').order_by('name').values_list('id', 'name'))
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
        state_list = list(State.objects.exclude(name='Uncategorized').values_list('id', 'name'))
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
    #state_list = list(State.objects.exclude(name='Uncategorized').values_list('id', 'name'))
    #state_list.insert(0, ('', '-- None --'))
    #state = forms.ChoiceField(choices = state_list, widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
    #district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'district field is required.'})
    #academic = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
    workshop_type = forms.ChoiceField(choices = [(0, 'Workshop (Default)'), (1, 'Pilot Workshop'), (2, 'Live Workshop')], widget=forms.Select(attrs = {}), required = False)
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
        self.fields['department'].choices = Department.objects.exclude(name='Uncategorized').values_list('id', 'name')

        foss_list = list(FossCategory.objects.all().values_list('id', 'foss'))
        foss_list.insert(0, ('', '-- None --'))
        lang_list = list(Language.objects.all().values_list('id', 'name'))
        lang_list.insert(0, ('', '-- None --'))
        self.fields['foss'].choices = foss_list
        self.fields['language'].choices = lang_list
        #if user:
        #    self.fields['state'].initial = user.organiser.academic.state.id
        #    self.fields['district'].choices = District.objects.filter(state =user.organiser.academic.state).values_list('id', 'name')
        #    self.fields['district'].initial = user.organiser.academic.district.id
        #    if args and 'district' in args[0]:
        #            choices = AcademicCenter.objects.filter(district =args[0]['district']).values_list('id', 'institution_name')
        #    else:
        #        choices = AcademicCenter.objects.filter(district =user.organiser.academic.district).values_list('id', 'institution_name')
        #        
        #    self.fields['academic'].choices = choices
        #    self.fields['academic'].initial = user.organiser.academic.id
        if instance:
            #self.fields['state'].initial = user.organiser.academic.state.id
            #self.fields['district'].choices = District.objects.filter(state =instance.academic.state).values_list('id', 'name')
            #self.fields['district'].initial = instance.academic.district.id
            #self.fields['academic'].choices = AcademicCenter.objects.filter(district =instance.academic.district).values_list('id', 'institution_name')
            #self.fields['academic'].initial = instance.academic_id
            self.fields['department'].initial = instance.department.all().values_list('id', flat=True)
            try:
                self.fields['wdate'].initial = str(instance.wdate) + " " + str(instance.wtime)[0:5]
            except Exception, e:
                print e
                self.fields['wdate'].initial = str(instance.trdate) + " " + str(instance.trtime)[0:5]
            self.fields['foss'].initial = instance.foss_id
            self.fields['language'].initial = instance.language_id
            self.fields['skype'].initial = instance.skype

class WorkshopPermissionForm(forms.Form):
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
    except:
        pass

class TestForm(forms.Form):
    #district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'district field is required.'})
    #academic = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
    choices = ()
    try:
        choices = list(TestCategory.objects.all().values_list('id', 'name'))
        choices.insert(0, ('', '-- None --'))
    except:
        pass
    test_category = forms.ChoiceField(choices = choices, widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'Category field is required.'})
    workshop = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False, error_messages = {'required':'Workshop field is required.'})
    training = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False, error_messages = {'required':'Training field is required.'})
    invigilator = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'invigilator Name field is required.'})
    dchoices = ()
    try:
        dchoices = list(Department.objects.all().values_list('id', 'name'))
        dchoices.insert(0, ('', '-- None --'))
    except:
        pass
    department = forms.MultipleChoiceField(choices = dchoices, widget=forms.SelectMultiple(attrs = {}), required = True, error_messages = {'required':'Department Name field is required.'})
    tdate = forms.DateTimeField(required = True, error_messages = {'required':'Date field is required.'})
    fchoices = []
    try:
        fchoices = list(FossCategory.objects.all().values_list('id', 'foss'))
        fchoices.insert(0, ('', '-- None --'))
    except:
        pass
    foss = forms.ChoiceField(choices = fchoices, widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'Foss Name field is required.'})
    def __init__(self, *args, **kwargs):
        user = None
        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]
        instance = None
        if 'instance' in kwargs:
            instance = kwargs["instance"]
            del kwargs["instance"]
        super(TestForm, self).__init__(*args, **kwargs)
        #choices data 
        self.fields['department'].choices = Department.objects.exclude(name='Uncategorized').values_list('id', 'name')

        if user:
            #print "i am in user"
            #self.fields['district'].choices = District.objects.filter(state =user.organiser.academic.state).values_list('id', 'name')
            #self.fields['district'].initial = user.organiser.academic.district.id
            #if args and 'district' in args[0]:
            #        choices = AcademicCenter.objects.filter(district =args[0]['district']).values_list('id', 'institution_name')
            #else:
            #    choices = AcademicCenter.objects.filter(district =user.organiser.academic.district).values_list('id', 'institution_name')
            #    
            #self.fields['academic'].choices = choices
            #self.fields['academic'].initial = user.organiser.academic.id
            if instance:
                #print "i am in instance"
                wchoices = list(Workshop.objects.filter(academic = instance.academic, status = 2).values_list('id', 'workshop_code'))
                trchoices = list(Training.objects.filter(academic = instance.academic, status = 2).values_list('id', 'training_code'))
            else:
                try:
                    wchoices = list(Workshop.objects.filter(academic = user.organiser.academic, status = 2).values_list('id', 'workshop_code'))
                    wchoices.insert(0, ('', '-- None --'))
                    trchoices = list(Training.objects.filter(academic = user.organiser.academic, status = 2).values_list('id', 'training_code'))
                    trchoices.insert(0, ('', '-- None --'))
                except:
                    i = Invigilator.objects.get(user_id = args[0]['invigilator']) 
                    wchoices = list(Workshop.objects.filter(academic = i.academic, status = 2).values_list('id', 'workshop_code'))
                    wchoices.insert(0, ('', '-- None --'))
                    trchoices = list(Training.objects.filter(academic = i.academic, status = 2).values_list('id', 'training_code'))
                    trchoices.insert(0, ('', '-- None --'))
            self.fields['workshop'].choices = wchoices
            self.fields['training'].choices = trchoices
            
            if instance:
                invigilators = Invigilator.objects.filter(academic  = instance.academic, status=1).exclude(user_id = user.id)
            else:
                try:
                    invigilators = Invigilator.objects.filter(academic  = user.organiser.academic, status=1).exclude(user_id = user.id)
                except:
                    i = Invigilator.objects.get(user_id = args[0]['invigilator'])
                    invigilators = Invigilator.objects.filter(academic  = i.academic, status=1).exclude(user_id = user.id)
            ichoices = []
            for i in invigilators:
                ichoices.insert(0, (i.user_id, i.user.username))
            ichoices.insert(0, ('', '-- None --'))
            self.fields['invigilator'].choices = ichoices
        
        if args:
            #print "i am in arg"
            if 'test_category' in args[0]:
                if args[0]['test_category'] and args[0]['test_category'] != '' and args[0]['test_category'] != 'None':
                    if int(args[0]['test_category']) == 1:
                        if 'workshop' in args[0]:
                            if args[0]['workshop'] and args[0]['workshop'] != '' and args[0]['workshop'] != 'None':
                                w = Workshop.objects.get(pk=args[0]['workshop'])
                                choices = (('', '-- None --'), (w.foss_id, w.foss.foss),)
                                self.fields['foss'].choices = choices
                                if 'edit' in args:
                                    self.fields['department'].choices = Department.objects.all().values_list('id', 'name')
                                else:
                                    self.fields['department'].choices = w.department.select_related().values_list('id', 'name')
                                    
                    if int(args[0]['test_category']) == 2:
                        if 'training' in args[0]:
                            if args[0]['training'] and args[0]['training'] != '' and args[0]['training'] != 'None':
                                w = Training.objects.get(pk=args[0]['training'])
                                choices = (('', '-- None --'), (w.foss_id, w.foss.foss),)
                                self.fields['foss'].choices = choices
                                if 'edit' in args:
                                    self.fields['department'].choices = Department.objects.all().values_list('id', 'name')
                                else:
                                    self.fields['department'].choices = w.department.select_related().values_list('id', 'name')
                    
        if instance:
            #print "I am in instance"
            #self.fields['district'].choices = District.objects.filter(state =instance.academic.state).values_list('id', 'name')
            #self.fields['district'].initial = instance.academic.district.id
            #self.fields['academic'].choices = AcademicCenter.objects.filter(district =instance.academic.district).values_list('id', 'institution_name')
            #self.fields['academic'].initial = instance.academic_id
            self.fields['test_category'].initial = instance.test_category_id
            self.fields['department'].initial = instance.department.all().values_list('id', flat=True)
            self.fields['tdate'].initial = str(instance.tdate) + " " + str(instance.ttime)[0:5]
            self.fields['workshop'].initial = instance.workshop_id
            self.fields['invigilator'].initial = instance.invigilator_id
            
            fchoices = []
            test = Test.objects.filter(pk=instance.id)
            if test:
                fchoices.insert(0, (test[0].foss_id, test[0].foss.foss))
            fchoices.insert(0, ('', '-- None --'))
            self.fields['foss'].choices = fchoices
            self.fields['foss'].initial = instance.foss_id

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

class TrainingForm(forms.Form):
    department = forms.MultipleChoiceField(choices = [('', '-- None --'),], widget=forms.SelectMultiple(attrs = {}), required = True, error_messages = {'required':'Department Name field is required.'})
    try:
        course = forms.ChoiceField(choices = [('', '-- None --')] + list(Course.objects.all().values_list('id', 'name')), required = True, error_messages = {'required':'Course Name field is required.'})
    except:
        pass
    course_number = forms.CharField()
    batch = forms.ChoiceField(choices = [('', '-- None --'), (1, '1st Semester'), (2, '2ed Semester'), (3, '3ed Semester'), (4, '4th Semester'), (5, '5th Semester'), (6, '6th Semester'), (7, '7th Semester'), (8, '8th Semester')], required = True, error_messages = {'required':'Batch Name field is required.'})
    free_lab_hours = forms.ChoiceField(widget=forms.RadioSelect, choices=[(0, 'No'),(1, 'Yes')], required = True)
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
        super(TrainingForm, self).__init__(*args, **kwargs)
        #choices data 
        self.fields['department'].choices = Department.objects.exclude(name='Uncategorized').values_list('id', 'name')

        foss_list = list(FossCategory.objects.all().values_list('id', 'foss'))
        foss_list.insert(0, ('', '-- None --'))
        lang_list = list(Language.objects.all().values_list('id', 'name'))
        lang_list.insert(0, ('', '-- None --'))
        self.fields['foss'].choices = foss_list
        self.fields['language'].choices = lang_list

        if instance:
            self.fields['department'].initial = instance.department.all().values_list('id', flat=True)
            self.fields['wdate'].initial = str(instance.trdate) + " " + str(instance.trtime)[0:5]
            self.fields['course'].initial = instance.course.id
            self.fields['batch'].initial = instance.batch
            self.fields['course_number'].initial = instance.course_number
            self.fields['free_lab_hours'].initial = instance.free_lab_hours
            self.fields['foss'].initial = instance.foss_id
            self.fields['language'].initial = instance.language_id
            self.fields['skype'].initial = instance.skype
