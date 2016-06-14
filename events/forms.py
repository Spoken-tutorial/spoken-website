
# Third Party Stuff
from django import forms
from django.contrib.auth.models import User

# Spoken Tutorial Stuff
from events.formsv2 import *
from events.models import *


class RpForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='Resource Person'))
    state = forms.ModelChoiceField(queryset=State.objects.all())
    status = forms.BooleanField(required=False)

    class Meta:
        model = ResourcePerson
        exclude = ['assigned_by']


class AcademicForm(forms.ModelForm):
    state = forms.ModelChoiceField(label='State', cache_choices=True, widget=forms.Select(attrs={'class': 'ac-state'}), queryset=State.objects.order_by(
        'name'), empty_label="--- None ---", help_text="", error_messages={'required': 'State field required.'})

    university = forms.ModelChoiceField(label='University', cache_choices=True, widget=forms.Select(
        attrs={'class': 'ac-university'}), queryset=University.objects.none(), empty_label="--- None ---", help_text="", error_messages={'required': 'University field required.'})

    district = forms.ModelChoiceField(label='Dist', cache_choices=True, widget=forms.Select(attrs={'class': 'ac-district'}), queryset=District.objects.none(
    ), empty_label="--- None ---", help_text="", error_messages={'required': 'Institute Type field required.'})

    city = forms.ModelChoiceField(label='City', cache_choices=True, widget=forms.Select(
        attrs={'class': 'ac-city'}), queryset=City.objects.none(), empty_label="--- None ---", help_text="", error_messages={'required': 'City Type field required.'})

    location = forms.ModelChoiceField(label='Location', cache_choices=True, widget=forms.Select(attrs={'class': 'ac-location'}), queryset=Location.objects.none(
    ), empty_label="--- None ---", help_text="", error_messages={'required': 'City Type field required.'}, required=False)

    contact_person = forms.CharField(widget=forms.Textarea(attrs={'rows': '5'}), required=False)
    remarks = forms.CharField(widget=forms.Textarea(attrs={'rows': '5'}), required=False)
    rating = forms.ChoiceField(choices=(('1', 'Rating 1'), ('2', 'Rating 2'),
                                        ('3', 'Rating 3'), ('4', 'Rating 4'), ('5', 'Rating 5')))

    def __init__(self, user, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]

        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]

        super(AcademicForm, self).__init__(*args, **kwargs)
        # initial
        self.fields["state"].queryset = State.objects.filter(resourceperson__user=user, resourceperson__status=1)
        # prevent ajax loaded data
        if args:
            # if 'district' in args[0]:
            #    if args[0]['district'] and args[0]['district'] != '' and args[0]['district'] != 'None':
            #        self.fields["location"].queryset = Location.objects.filter(district__id=args[0]['district'])
            #
            if 'state' in args[0]:
                if args[0]['state'] != '' and args[0]['state'] != 'None':
                    self.fields["university"].queryset = University.objects.filter(state__id=args[0]['state'])
                    self.fields["district"].queryset = District.objects.filter(state__id=args[0]['state'])
                    self.fields["city"].queryset = City.objects.filter(state__id=args[0]['state'])
        # for edit
        if initial:
            if args and 'state' in args[0]:
                if args[0]['state'] != '' and args[0]['state'] != 'None':
                    self.fields["university"].queryset = University.objects.filter(state__id=args[0]['state'])
                self.fields["district"].queryset = District.objects.filter(state__id=args[0]['state'])
                self.fields["city"].queryset = City.objects.filter(state__id=args[0]['state'])
            else:
                self.fields["university"].queryset = University.objects.filter(state__id=initial.state_id)
                self.fields["district"].queryset = District.objects.filter(state__id=initial.state_id)
                self.fields["city"].queryset = City.objects.filter(state__id=initial.state_id)

    class Meta:
        model = AcademicCenter
        exclude = ['user', 'academic_code', 'institute_category']


class OrganiserForm(forms.Form):
    state = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}),
                              required=True, error_messages={'required': 'State field is required.'})
    college = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}),
                                required=True, error_messages={'required': 'College Name field is required.'})

    def __init__(self, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]

        super(OrganiserForm, self).__init__(*args, **kwargs)
        # load the choices
        state_list = list(State.objects.exclude().order_by('name').values_list('id', 'name'))
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
            self.fields['college'].choices = AcademicCenter.objects.filter(
                district_id=initial.academic.district_id).values_list('id', 'institution_name')
            # initial data
            self.fields['college'].initial = initial.academic_id


class InvigilatorForm(forms.Form):
    state = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}),
                              required=True, error_messages={'required': 'State field is required.'})
    college = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}),
                                required=True, error_messages={'required': 'College Name field is required.'})

    def __init__(self, *args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]

        super(InvigilatorForm, self).__init__(*args, **kwargs)
        # load the choices
        state_list = list(State.objects.exclude().values_list('id', 'name'))
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
            self.fields['college'].choices = AcademicCenter.objects.filter(
                district_id=initial.academic.district_id).values_list('id', 'institution_name')
            # initial data
            self.fields['college'].initial = initial.academic_id


class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department
        exclude = ['created', 'updated']


class TrainingForm(forms.ModelForm):
    user = None

    class Meta:
        model = Training
        exclude = ['status', 'participant_count', 'extra_fields',
                   'organiser', 'academic', 'training_code', 'ttime', 'appoved_by']

    def clean_course_number(self):
        super(TrainingForm, self).clean()
        if 'training_type' in self.cleaned_data:
            if self.cleaned_data['training_type'] == '0' and self.cleaned_data['course_number'] == '':
                raise forms.ValidationError("Course Number field is required.")
    # Organiser training count restrict

    def clean_tdate(self):
        super(TrainingForm, self).clean()
        organiser = self.user.organiser
        tdate = self.cleaned_data['tdate']
        training_count = Training.objects.filter(tdate=tdate, organiser=organiser).count()
        if training_count >= 3:
            raise ValidationError(
                "Organiser cannot schedule more than 3 software training workshops per day.  Kindly choose other dates for other training workshops")
        return self.cleaned_data['tdate']

    training_type = forms.ChoiceField(widget=forms.RadioSelect, choices=[(0, 'Training'), ], required=True)
    course_number = forms.CharField(required=True)
    no_of_lab_session = forms.ChoiceField(widget=forms.Select, choices=[('', '---------'), ('1', 'Semester I'), ('2', 'Semester II'), (
        '3', 'Semester III'), ('4', 'Semester IV'), ('5', 'Semester V'), ('6', 'Semester VI'), ('7', 'Semester VII'), ('8', 'Semester VIII')], required=True)

    department = forms.ModelMultipleChoiceField(label='Department', cache_choices=True, widget=forms.SelectMultiple(attrs={}), queryset=Department.objects.exclude(
        name='Uncategorised').order_by('name'), help_text="", error_messages={'required': 'Department field required.'})

    foss = forms.ModelChoiceField(label='Foss', cache_choices=True, widget=forms.Select(attrs={}), queryset=FossCategory.objects.filter(
        status=1, id__in=FossAvailableForWorkshop.objects.filter(status=1).values_list('foss').distinct()).order_by('foss'), help_text="", error_messages={'required': 'Foss field required.'})

    language = forms.ModelChoiceField(label='Language', cache_choices=True, widget=forms.Select(attrs={}), queryset=Language.objects.filter(
        id__in=FossAvailableForWorkshop.objects.all().values_list('language').distinct()).order_by('name'), help_text="", error_messages={'required': 'Language field required.'})

    tdate = forms.DateTimeField(required=True, error_messages={'required': 'Timing field is required.'})
    skype = forms.ChoiceField(widget=forms.RadioSelect, choices=[(0, 'No'), (1, 'Yes')], required=True)
    xml_file = forms.FileField(required=True)

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs["user"]
            del kwargs["user"]
        instance = ''
        if 'instance' in kwargs:
            instance = kwargs["instance"]
            del kwargs["instance"]
        super(TrainingForm, self).__init__(*args, **kwargs)
        if self.user:
            if instance:
                self.fields['xml_file'].required = False
            from events.views import is_resource_person
            if is_resource_person(self.user):
                self.fields['training_type'].choices = [(0, 'Training'), (2, 'Pilot Workshop'), (3, 'Live Workshop')]
            self.fields['training_type'].initial = 0
        if instance:
            self.fields['training_type'].initial = instance.training_type
            self.fields['course'].initial = instance.course_id
            self.fields['foss'].initial = instance.foss
            self.fields['language'].initial = instance.language
            self.fields['tdate'].initial = str(instance.tdate) + " " + str(instance.ttime)[0:5]
            self.fields['department'].initial = instance.department.all().values_list('id', flat=True)
            self.fields['skype'].initial = instance.skype
            if instance.extra_fields:
                self.fields['course_number'].initial = instance.extra_fields.paper_name
                self.fields['no_of_lab_session'].initial = instance.extra_fields.no_of_lab_session


class TrainingPermissionForm(forms.Form):
    try:
        permission_choices = list(PermissionType.objects.all().values_list('id', 'name'))
        permission_choices.insert(0, ('', '-- None --'))
        permissiontype = forms.ChoiceField(choices=permission_choices, widget=forms.Select(attrs={}), required=True)

        user_list = list(User.objects.filter(groups__name='Workshop Permission').values_list('id', 'username'))
        user_list.insert(0, ('', '-- None --'))
        user = forms.ChoiceField(choices=user_list, widget=forms.Select(attrs={}), required=True)

        state_list = list(State.objects.exclude(name='Uncategorised').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        state = forms.ChoiceField(choices=state_list, widget=forms.Select(attrs={}), required=True)

        district = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}),
                                     required=False, error_messages={'required': 'district field is required.'})

        university = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}), required=False)

        institution_type = list(InstituteType.objects.order_by('name').values_list('id', 'name'))
        institution_type.insert(0, ('', '-- None --'))
        institutiontype = forms.ChoiceField(choices=institution_type, widget=forms.Select(attrs={}), required=False)

        institute = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}), required=False)

        def __init__(self, *args, **kwargs):
            super(TrainingPermissionForm, self).__init__(*args, **kwargs)
            if args:
                if 'state' in args[0] and 'district' in args[0]:
                    if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                        choices = list(District.objects.filter(state_id=args[0]['state']).values_list('id', 'name'))
                        choices.insert(0, ('', '-- None --'))
                        self.fields['district'].choices = choices

                if 'state' in args[0] and 'university' in args[0]:
                    if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                        choices = list(University.objects.filter(state_id=args[0]['state']).values_list('id', 'name'))
                        choices.insert(0, ('', '-- None --'))
                        self.fields['university'].choices = choices

                if 'district' in args[0] and 'institute' in args[0]:
                    if args[0]['district'] and args[0]['district'] != '' and args[0]['district'] != 'None':
                        choices = list(AcademicCenter.objects.filter(district_id=args[0][
                                       'district']).values_list('id', 'institution_name'))
                        choices.insert(0, ('', '-- None --'))
                        self.fields['institute'].choices = choices
    except:
        pass


class TestForm(forms.ModelForm):

    class Meta:
        model = Test
        exclude = ['status', 'participant_count', 'organiser', 'academic',
                   'test_code', 'ttime', 'training', 'workshop', 'appoved_by']

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
    test_category = forms.ModelChoiceField(queryset=TestCategory.objects.filter(status=True), required=False)
    tdate = forms.DateTimeField(required=True, error_messages={'required': 'Date field is required.'})
    # workshop = forms.ChoiceField(choices = [('', '-- None --'),], widget=forms.Select(attrs = {}), required = False, error_messages = {'required':'Workshop field is required.'})
    training = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs={}),
                                 required=False, error_messages={'required': 'Training field is required.'})
    foss = forms.ModelChoiceField(label='Foss', cache_choices=True, widget=forms.Select(attrs={}), queryset=FossCategory.objects.filter(
        id__in=FossAvailableForTest.objects.filter(status=1).values_list('foss').distinct()).order_by('foss'), help_text="", error_messages={'required': 'Foss field required.'})
    department = forms.ModelMultipleChoiceField(label='Department', cache_choices=True, widget=forms.SelectMultiple(attrs={}), queryset=Department.objects.exclude(
        name='Uncategorised').order_by('name'), help_text="", error_messages={'required': 'Department field required.'})

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
                self.fields['invigilator'].queryset = Invigilator.objects.filter(
                    academic=user.organiser.academic, status=1).exclude(user_id=user.id)
                trainings = TrainingRequest.test_training.filter(
                    training_planner__academic=user.organiser.academic, training_planner__organiser=user.organiser)
                trchoices = []
                for training in trainings:
                    if training.batch:
                        if training.get_partipants_from_attendance():
                            trchoices.append((training.id, training.training_name()))
                    else:
                        trchoices.append((training.id, training.training_name()))
                trchoices.insert(0, ('', '-------'))
                if instance:
                    trchoices.insert(0, (instance.training_id, instance.training.training_name()))
                self.fields['training'].choices = trchoices
            except:
                pass

        if instance:
            self.fields['invigilator'].queryset = Invigilator.objects.filter(
                academic=instance.organiser.academic, status=1).exclude(user_id=user.id)
            self.fields['invigilator'].initial = instance.invigilator
            self.fields['test_category'].initial = instance.test_category
            self.fields['foss'].initial = instance.foss
            self.fields['tdate'].initial = str(instance.tdate) + " " + str(instance.ttime)[0:5]
            self.fields['department'].initial = instance.department.all().values_list('id', flat=True)
            if instance.test_category.id == 2:
                self.fields['training'].initial = instance.training_id


class TrainingScanCopyForm(forms.Form):
    scan_copy = forms.FileField(label='Select a Scaned copy', required=True)

    def clean(self):
        super(TrainingScanCopyForm, self).clean()
        file_type = ['application/pdf']
        if 'scan_copy' in self.cleaned_data:
            if component.content_type not in file_type:
                raise forms.ValidationError("You have forgotten about Fred!")
        else:
            raise forms.ValidationError("You have forgotten about Fred!")


class ParticipantSearchForm(forms.Form):
    email = forms.EmailField(required=False)
    username = forms.CharField(required=False)


class TrainingCompletionForm(forms.Form):
    approximate_hour = forms.ChoiceField(
        choices=[('', '---------'), (0, '0 - 5'), (1, '6 - 10'), (2, '11 - 15'), (3, '16 - 20'), (4, ' > 20')])
    online_test = forms.ChoiceField(choices=[('', '---------'), (0, 'Will Request'),
                                             (1, 'Will not Request'), (2, 'Already Requested')])
    is_tutorial_useful = forms.ChoiceField(widget=forms.RadioSelect, choices=[(1, 'Yes'), (0, 'No')])
    future_training = forms.ChoiceField(widget=forms.RadioSelect, choices=[(1, 'Yes'), (0, 'No')])
    recommend_to_others = forms.ChoiceField(widget=forms.RadioSelect, choices=[(1, 'Yes'), (0, 'No')])

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            del kwargs["user"]
        super(TrainingCompletionForm, self).__init__(*args, **kwargs)
#        if user:
#            if user.organiser.test_organiser.filter(status=4).count():
#                self.fields['online_test'].choices=[('', '---------'), (0, 'Will Request'), (1, 'Will not Request')]


class LiveFeedbackForm(forms.ModelForm):
    fiveChoice = (('1', '',), ('2', '',), ('3', '',), ('4', '',), ('5', '',))
    threeChoice = (('1', '',), ('2', '',), ('3', '',))

    name = forms.CharField()
    email = forms.EmailField()
    branch = forms.CharField()
    institution = forms.CharField()

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
        model = TrainingLiveFeedback
        exclude = ['training', 'mdluser_id']


class TrainingLanguageFeedbackForm(forms.ModelForm):
    fiveChoice = ((1, ''), (2, ''), (3, ''), (4, ''), (5, ''))
    # name = forms.CharField()
    age = forms.CharField()

    medium_of_instruction = forms.ChoiceField(
        widget=forms.RadioSelect, choices=((0, 'English'), (1, "Vernacular Medium")))
    gender = forms.ChoiceField(widget=forms.RadioSelect, choices=((0, 'Male'), (1, "Female")))

    language_prefered = forms.ModelChoiceField(cache_choices=True, widget=forms.Select(attrs={}), queryset=Language.objects.order_by(
        'name'), empty_label="--- None ---", error_messages={'required': 'Language field required.'})

    tutorial_was_useful = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    learning_experience = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    satisfied_with_learning_experience = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    concept_explain_clearity = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    overall_learning_experience = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    user_interface = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    understanding_difficult_concept = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    curious_and_motivated = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    similar_tutorial_with_other_content = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    foss_tutorial_was_mentally_demanding = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    side_by_side_method_is_understood = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)

    compfortable_learning_in_language = forms.ChoiceField(widget=forms.RadioSelect, choices=((1, 'Least comfortable'), (
        2, 'Less comfortable'), (3, 'Neither comfortable nor uncomfortable'), (4, 'Comfortable'), (5, 'Extremely comfortable')))
    confidence_level_in_language = forms.ChoiceField(widget=forms.RadioSelect, choices=((1, 'Least confident'), (
        2, 'Less confident'), (3, 'Neither confident nor unconfident'), (4, 'Very confident'), (5, 'Extremely confident')))
    preferred_language = forms.ChoiceField(widget=forms.RadioSelect, choices=((0, 'English'), (0, 'Indian Language')))
    preferred_language_reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    prefer_translation_in_mother_tongue = forms.ChoiceField(widget=forms.RadioSelect, choices=((1, 'Yes'), (0, 'No')))
    prefer_translation_in_mother_tongue_reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    side_by_side_method_meant = forms.ChoiceField(widget=forms.RadioSelect, choices=((1, 'Yes'), (0, 'No')))
    side_by_side_method_is_beneficial = forms.ChoiceField(widget=forms.RadioSelect, choices=((1, 'Yes'), (0, 'No')))
    side_by_side_method_is_beneficial_reason = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    side_by_side_method_is_effective = forms.ChoiceField(widget=forms.RadioSelect, choices=((1, 'Yes'), (0, 'No')))
    side_by_side_method_is = forms.ChoiceField(widget=forms.RadioSelect, choices=(
        (1, 'Effective because it allows to see the video and practice the software simultaneously'), (0, 'Is not effective for me as I like to see one window at a time')))
    limitations_of_side_by_side_method = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    content_information_flow = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    content_appropriate_examples = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    content_ease_of_understanding = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    content_clarity_of_instruction_sheet = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    content_ease_of_performing_assignment = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    content_best_features = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    content_areas_of_improvement = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    video_audio_video_synchronization = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    video_attractive_color_features = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    video_text_readable = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    video_best_features = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    video_areas_of_improvement = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    audio_pleasant_speech_and_accent = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    audio_soothing_and_friendly_tone = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    audio_understandable_and_clear_speech = forms.ChoiceField(widget=forms.RadioSelect, choices=fiveChoice)
    audio_best_features = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))
    audio_areas_of_improvement = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

    class Meta:
        model = TrainingLanguageFeedback
        exclude = ['name', 'training', 'mdluser_id']

    def __init__(self, *args, **kwargs):
        if 'training' in kwargs:
            del kwargs["training"]
        super(TrainingLanguageFeedbackForm, self).__init__(*args, **kwargs)


class TrainingReUseForm(forms.Form):
    user = None
    foss = forms.ModelChoiceField(label='Foss', cache_choices=True, widget=forms.Select(attrs={}), queryset=FossCategory.objects.filter(
        status=1, id__in=FossAvailableForWorkshop.objects.filter(status=1).values_list('foss').distinct()).order_by('foss'), help_text="", error_messages={'required': 'Foss field required.'})

    language = forms.ModelChoiceField(label='Language', cache_choices=True, widget=forms.Select(attrs={}), queryset=Language.objects.filter(
        id__in=FossAvailableForWorkshop.objects.all().values_list('language').distinct()).order_by('name'), help_text="", error_messages={'required': 'Language field required.'})

    tdate = forms.DateTimeField(required=True, error_messages={'required': 'Timing field is required.'})

    def clean_tdate(self):
        super(TrainingReUseForm, self).clean()
        organiser = self.user.organiser
        tdate = self.cleaned_data['tdate']
        training_count = Training.objects.filter(tdate=tdate, organiser=organiser).count()
        if training_count >= 3:
            raise ValidationError(
                "Organiser cannot schedule more than 3 software training workshops per day.  Kindly choose other dates for other training workshops")
        return self.cleaned_data['tdate']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TrainingReUseForm, self).__init__(*args, **kwargs)
