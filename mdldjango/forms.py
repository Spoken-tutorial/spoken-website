
from django import forms

#import Model form
from django.forms import ModelForm

#import events models
from events.models import *
from django.contrib.auth.models import User, Group

class OfflineDataForm(forms.Form):
    #workshop_code = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'Workshop field is required.'})
    xml_file  = forms.FileField(required=True)
    
    #def __init__(self,user, *args, **kwargs):
    #    super(OfflineDataForm, self).__init__(*args, **kwargs)
    #    #load the choices
    #    workshop_list = list(Workshop.objects.filter(organiser_id=user.id, status = 1).values_list('id', 'workshop_code'))
    #    workshop_list.insert(0, ('', '-- None --'))
    #    self.fields['workshop_code'].choices = workshop_list

class RegisterForm(forms.Form):
    state = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'State field is required.'})
    district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'district field is required.'})
    college = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'College Name field is required.'})
    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())
    course = forms.ChoiceField(choices = (('', '-- None --'), (1, 'B.E'), (2, 'MCA'),))
    year = forms.ChoiceField(choices = (('', '-- None --'), (1, '1st Year'), (2, '2ed year'),))
    
    def clean_username(self):
        username = self.cleaned_data['username']
        error = 0
        try:
            user = MdlUser.objects.filter(username=username).first().id
            error = 1
        except:
            return username
        if error:
            raise forms.ValidationError(u'Username: %s already exists' % username )
        
    def clean_email(self):
        email = self.cleaned_data['email']
        error = 0
        try:
            user = MdlUser.objects.filter(email=email).first().id
            error = 1
        except Exception, e:
            return email
        if error:
            raise forms.ValidationError( u'Email: %s already exists' % email )
        
    def clean(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return self.cleaned_data
        
    def __init__(self, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]
            
        super(RegisterForm, self).__init__(*args, **kwargs)
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

class FeedbackForm(forms.ModelForm):
    fiveChoice = (('1', '',), ('2', '',), ('3', '',), ('4', '',), ('5', '',))
    threeChoice = (('1', '',), ('2', '',), ('3', '',))
    content = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    sequence = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    clarity = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    interesting = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    appropriate_example = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    instruction_sheet = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    assignment = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    
    pace_of_tutorial = forms.ChoiceField(widget=forms.RadioSelect, choices = threeChoice )
    rate_workshop = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    workshop_learnt = forms.CharField(widget=forms.Textarea)
    weakness_workshop = forms.BooleanField(label='Duration of the workshop is less', required=False, initial=False)
    weakness_narration = forms.BooleanField(label='Pace of the narration in the tutorials was very fast', required=False, initial=False)
    weakness_understand = forms.BooleanField(label='Had to listen more than two times to understand the commands', required=False, initial=False)
    other_weakness = forms.CharField(widget=forms.Textarea)
    tutorial_language = forms.ChoiceField(widget=forms.RadioSelect, choices = threeChoice )
    apply_information = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    use_information = forms.CharField(widget=forms.Textarea)
    
    setup_learning = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    computers_lab = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    audio_quality = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    video_quality = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )

    workshop_orgainsation = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    faciliate_learning = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    motivate_learners = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    time_management = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )

    knowledge_about_software = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    provide_clear_explanation = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    answered_questions = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    interested_helping = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    executed_workshop = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    
    recommend_workshop = forms.ChoiceField(widget=forms.RadioSelect, choices = fiveChoice )
    use_information = forms.CharField(widget=forms.Textarea)
    other_comments = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = TrainingFeedback
        exclude = ['workshop', 'mdluser_id']

class PasswordResetForm(forms.Form):
    email = forms.EmailField()
    def clean_email(self):
        email = self.cleaned_data['email']
        error = 1
        try:
            user = MdlUser.objects.filter(email=email).first()
            if user:
                error = 0
        except Exception, e:
            print e
        if error:
            raise forms.ValidationError( u'Email: %s not exists' % email )
