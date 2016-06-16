
# Third Party Stuff
from captcha.fields import ReCaptchaField
from django import forms
from get_or_create_participant import encript_password

# Spoken Tutorial Stuff
from events.models import *
from events.signals import get_or_create_user


class OfflineDataForm(forms.Form):
    xml_file = forms.FileField(required=True)

    def clean(self):
        # super(OfflineDataForm, self).clean()
        # file_types = ['text']
        # if 'xml_file' in self.cleaned_data and self.cleaned_data['xml_file']:
        #     if not self.cleaned_data['xml_file'].content_type.split('/')[0] in file_types:
        #         raise forms.ValidationError("Not a valid file format.")
        # else:
        #    raise forms.ValidationError("Not a valid file format.")
        return self.cleaned_data


class RegisterForm(forms.Form):
    state = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}),
                              required=True, error_messages={'required': 'State field is required.'})
    # district = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = True, error_messages = {'required':'district field is required.'})
    college = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}),
                                required=True, error_messages={'required': 'College Name field is required.'})
    firstname = forms.CharField()
    lastname = forms.CharField()
    email = forms.EmailField()
    gender = forms.ChoiceField(widget=forms.RadioSelect, choices=[
                               ('Male', 'Male'), ('Female', 'Female')], required=True)
    password = forms.CharField(widget=forms.PasswordInput())
    password_confirm = forms.CharField(widget=forms.PasswordInput())
    year = forms.ChoiceField(choices=(('', '-- None --'),
                                      (1, '1st Year'),
                                      (2, '2nd year'),
                                      (3, '3rd year'),
                                      (4, '4th year'),
                                      (5, '5th year'),
                                      (6, '6th year'),
                                      (7, 'Others'),))
    captcha = ReCaptchaField()

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            MdlUser.objects.get(username=username)
            raise forms.ValidationError(u'Username: %s already exists' % username)
        except MdlUser.DoesNotExist:
            pass

        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        error = 0
        try:
            user = MdlUser.objects.filter(email=email).first()
            user.id
            error = 1
            # check if user exists
            mdluser, flag, authuser = get_or_create_user(user)
            if flag:
                mdluser.password = encript_password(mdluser.firstname)
                mdluser.save()
                # send email along with password
        except Exception:
            return email
        if error:
            raise forms.ValidationError(u'Email: %s already exists' % email)

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
        self.fields['course'] = forms.ChoiceField(
            choices=[('', '-- None --')] + list(Course.objects.order_by('name').values_list('id', 'name')))

        # load the choices
        state_list = list(State.objects.exclude(name='Uncategorised').order_by('name').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        self.fields['state'].choices = state_list
        if args:
            if 'state' in args[0]:
                if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                    choices = list(AcademicCenter.objects.filter(state_id=args[0][
                                   'state']).values_list('id', 'institution_name'))
                    choices.insert(0, ('', '-- None --'))
                    self.fields['college'].choices = choices
                    self.fields['college'].widget.attrs = {}
        if initial:
            self.fields['state'].initial = initial.academic.state_id
            # self.fields['district'].choices = District.objects.filter(state_id =initial.academic.state_id).values_list('id', 'name')
            self.fields['college'].choices = AcademicCenter.objects.filter(
                district_id=initial.academic.district_id).values_list('id', 'institution_name')
            # initial data
            # self.fields['district'].initial = initial.academic.district_id
            self.fields['college'].initial = initial.academic_id


class FeedbackForm(forms.ModelForm):
    fiveChoice = (('1', '',), ('2', '',), ('3', '',), ('4', '',), ('5', '',))
    threeChoice = (('1', '',), ('2', '',), ('3', '',))
    content = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    sequence = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    clarity = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    interesting = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    appropriate_example = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    instruction_sheet = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    assignment = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)

    pace_of_tutorial = forms.ChoiceField(widget=forms.RadioSelect, choices=threeChoice)
    rate_workshop = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    workshop_learnt = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    workshop_improved = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    weakness_workshop = forms.BooleanField(label='Duration of the workshop is less', required=False, initial=False)
    weakness_narration = forms.BooleanField(
        label='Pace of the narration in the tutorials was very fast', required=False, initial=False)
    weakness_understand = forms.BooleanField(
        label='Had to listen more than two times to understand the commands', required=False, initial=False)
    other_weakness = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    tutorial_language = forms.ChoiceField(widget=forms.RadioSelect, choices=threeChoice)
    apply_information = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    if_apply_information_yes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    setup_learning = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    computers_lab = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    audio_quality = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    video_quality = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)

    workshop_orgainsation = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    faciliate_learning = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    motivate_learners = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    time_management = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)

    knowledge_about_software = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    provide_clear_explanation = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    answered_questions = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    interested_helping = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    executed_workshop = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)

    recommend_workshop = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    reason_why = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    other_comments = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = TrainingFeedback
        exclude = ['training', 'mdluser_id']


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
            raise forms.ValidationError(u'Email: %s not exists' % email)
