# Standard Library
import datetime

# Third Party Stuff
from django import forms

# Spoken Tutorial Stuff
from creation.models import FossAvailableForWorkshop
from events.helpers import get_academic_years
from events.models import *


class StudentBatchForm(forms.ModelForm):
    year = forms.ChoiceField(choices=get_academic_years())
    csv_file = forms.FileField(required=True)

    class Meta:
        model = StudentBatch
        exclude = ['academic', 'stcount', 'organiser']


class NewStudentBatchForm(forms.ModelForm):
    csv_file = forms.FileField(required=True)

    class Meta:
        model = StudentBatch
        exclude = ['academic', 'year', 'department', 'stcount', 'organiser']


class UpdateStudentBatchForm(forms.ModelForm):
    year = forms.ChoiceField(choices=get_academic_years())

    class Meta:
        model = StudentBatch
        exclude = ['academic', 'stcount', 'organiser']


class UpdateStudentYearBatchForm(forms.ModelForm):
    year = forms.ChoiceField(choices=get_academic_years())

    class Meta:
        model = StudentBatch
        exclude = ['academic', 'stcount', 'organiser', 'department']


class TrainingRequestForm(forms.ModelForm):
    department = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.none())
    course_type = forms.ChoiceField(required=True)

    # course_type = forms.ChoiceField(choices=[('', '---------'),
    #                                            (0, 'Software Course outside lab hours'),
    #                                            (1, 'Software Course mapped in lab hours'),
    #                                            (2, ' Software Course unmapped in lab hours')])
    course = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.none())
    batch = forms.ModelChoiceField(empty_label='---------', queryset=StudentBatch.objects.none())
    training_planner = forms.CharField()

    class Meta:
        model = TrainingRequest
        exclude = ['participants', 'status', 'training_planner']

    def clean(self):
        if self.cleaned_data:
            # 48hrs, batch id fetched
            batch_id_list = []
            sm_batch_all = StudentMaster.objects.all()
            for i in sm_batch_all:
                if datetime.datetime.today().isoformat() < (i.created + datetime.timedelta(days=2)).isoformat():
                    batch_id_list.append(i.batch_id)
            batch_id_set = set(batch_id_list)
            uniq_batch_id = []
            for j in batch_id_set:
                uniq_batch_id.append(j)
            #
            tp = TrainingPlanner.objects.get(pk=self.cleaned_data['training_planner'])
            '''if 'department' in self.cleaned_data and self.cleaned_data['department'] \
        and 'batch' in self.cleaned_data and self.cleaned_data['batch']:
        if tp.is_full(self.cleaned_data['department'], self.cleaned_data['batch']):
          raise forms.ValidationError("No. of training requests for this department exceeded.")

        if self.cleaned_data['batch'].id in uniq_batch_id:
          raise forms.ValidationError("You cannot add selected Master Batch prior to 48 hours of requesting STP.")

        if 'course_type' in self.cleaned_data and self.cleaned_data['course_type']:
          if tp.is_course_full(self.cleaned_data['course_type'],
                               self.cleaned_data['department'],
                               self.cleaned_data['batch']):
            raise forms.ValidationError("No. of training requests for selected course type exceeded")'''

            # Date restriction
            if self.cleaned_data and 'sem_start_date' in self.cleaned_data and self.cleaned_data['sem_start_date']:
                start_date, end_date = tp.get_current_semester_date_duration_new()
                if not (self.cleaned_data['sem_start_date'] <= end_date and
                        self.cleaned_data['sem_start_date'] >= start_date):
                    raise forms.ValidationError("Invalid semester start date")
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        course_type = kwargs.pop('course_type')
        super(TrainingRequestForm, self).__init__(*args, **kwargs)
        self.fields['course_type'].choices = course_type

        if kwargs and 'data' in kwargs:
            # Generating course list based on course type
            if 'course_type' in kwargs['data'] and kwargs['data']['course_type'] != '':
                courses = CourseMap.objects.filter(category=kwargs['data']['course_type'])
                choices = [('', '---------'), ]
                for course in courses:
                    choices.append((course.id, course.course_name()))
                self.fields['course'].queryset = CourseMap.objects.filter(category=kwargs['data']['course_type'])
                self.fields['course'].choices = choices
                self.fields['course'].initial = kwargs['data']['course']
            # Generating students batch list based on department
            if kwargs['data']['department'] != '':
                department = kwargs['data']['department']
                self.fields['batch'].queryset = StudentBatch.objects.filter(
                    academic_id=user.organiser.academic.id, stcount__gt=0, department_id=department)
                self.fields['batch'].initial = kwargs['data']['batch']
        # overwrite department choices
        self.fields['department'].queryset = Department.objects.filter(id__in=StudentBatch.objects.filter(
            academic=user.organiser.academic, stcount__gt=0).values_list('department_id'))


class TrainingRequestEditForm(forms.ModelForm):
    course_type = forms.ChoiceField(choices=[('', '---------'),
                                             (0, 'Software Course outside lab hours'),
                                             (1, 'Software Course mapped in lab hours'),
                                             (2, ' Software Course unmapped in lab hours')])
    course = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.none())
    training_planner = forms.CharField()

    class Meta:
        model = TrainingRequest
        exclude = ['participants', 'status', 'training_planner', 'department', 'batch']

    def clean(self):
        # Date restriction
        if self.cleaned_data and 'sem_start_date' in self.cleaned_data and self.cleaned_data['sem_start_date']:
            tp = TrainingPlanner.objects.get(pk=self.cleaned_data['training_planner'])
            start_date, end_date = tp.get_current_semester_date_duration_new()
            if not (self.cleaned_data['sem_start_date'] <= end_date and
                    self.cleaned_data['sem_start_date'] >= start_date):
                raise forms.ValidationError("Invalid semester start date")
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        training = kwargs.pop('training', None)
        kwargs.pop('user', None)
        super(TrainingRequestEditForm, self).__init__(*args, **kwargs)
        flag = True
        data = kwargs.pop('data', None)
        if data and 'course_type' in data:
            if data['course_type']:
                self.fields['course'].queryset = CourseMap.objects.filter(category=data['course_type'])
                if 'course' in data and data['course']:
                    self.fields['course'].initial = data['course']
            else:
                flag = False
        else:
            flag = False
        if not flag and training:
            self.fields['course_type'].initial = training.course.category
            self.fields['course'].queryset = CourseMap.objects.filter(category=training.course.category)
            self.fields['course'].initial = training.course_id
        flag = True
        if data and 'sem_start_date' in data:
            if data['sem_start_date']:
                self.fields['sem_start_date'].initial = data['sem_start_date']
            else:
                flag = False
        else:
            flag = False
        if not flag and training:
            self.fields['sem_start_date'].initial = training.sem_start_date


class CourseMapForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[('', '---------'),
                                          (1, 'Software Course mapped in lab hours'),
                                          (2, ' Software Course unmapped in lab hours')])
    course = forms.ModelChoiceField(queryset=LabCourse.objects.all())
    foss = forms.ModelChoiceField(
        queryset=FossCategory.objects.filter(
            id__in=FossAvailableForWorkshop.objects.filter(status=1).values('foss').distinct(),
            status=True
        )
    )

    class Meta:
        model = CourseMap
        exclude = ['test']

    def __init__(self, *args, **kwargs):
        super(CourseMapForm, self).__init__(*args, **kwargs)


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        exclude = ['password', 'last_login', 'is_superuser', 'username', 'is_staff',
                   'is_active', 'date_joined', 'groups', 'user_permissions', 'email']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)


class SingleTrainingForm(forms.ModelForm):
    training_type = forms.ChoiceField(choices=[('', '---------'), (0, 'School'),
                                               (3, 'Vocational'), (1, 'Live workshop'), (2, 'Pilot workshop')])
    csv_file = forms.FileField(required=True)

    class Meta:
        model = SingleTraining
        exclude = ['organiser', 'status', 'participant_count', 'total_participant_count']

    def __init__(self, *args, **kwargs):
        super(SingleTrainingForm, self).__init__(*args, **kwargs)
        self.fields['academic'].required = False
        self.fields['state'].required = False
        self.fields['institution_type'].required = False

    def clean(self):
                # self.cleaned_data['csv_file']
        if self.cleaned_data['csv_file'].name.split('.')[-1] == 'csv':
            pass
        else:
            raise forms.ValidationError("Invalid file format.")
        return self.cleaned_data

    def clean_tdate(self):
        today = datetime.datetime.now()
        tdate = self.cleaned_data['tdate']
        if today.date() > tdate:
            raise forms.ValidationError("Invalid semester training date")
        return tdate


class SingleTrainingEditForm(forms.ModelForm):
    training_type = forms.ChoiceField(choices=[('', '---------'), (0, 'School'),
                                               (3, 'Vocational'), (1, 'Live workshop'), (2, 'Pilot workshop')])
    csv_file = forms.FileField(required=False)

    class Meta:
        model = SingleTraining
        exclude = ['organiser', 'status', 'participant_count', 'total_participant_count']

    def __init__(self, *args, **kwargs):
        super(SingleTrainingEditForm, self).__init__(*args, **kwargs)
        self.fields['academic'].required = False
        self.fields['state'].required = False
        self.fields['institution_type'].required = False

    def clean(self):
            # self.cleaned_data['csv_file']
        if 'csv_file' in self.cleaned_data and self.cleaned_data['csv_file']:
            if self.cleaned_data['csv_file'].name.split('.')[-1] == 'csv':
                pass
            else:
                raise forms.ValidationError("Invalid file format.")
        return self.cleaned_data

    def clean_tdate(self):
        today = datetime.datetime.now()
        tdate = self.cleaned_data['tdate']
        if today.date() > tdate:
            raise forms.ValidationError("Invalid semester training date")
        return tdate


class OrganiserFeedbackForm(forms.ModelForm):
    offered_training_foss = forms.ModelMultipleChoiceField(
        queryset=FossCategory.objects.filter(status=1), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = OrganiserFeedback
        fields = '__all__'
        widgets = {'student_stream': forms.CheckboxSelectMultiple,
                   'language': forms.CheckboxSelectMultiple,
                   'trained_foss': forms.CheckboxSelectMultiple,
                   'helpful_for': forms.CheckboxSelectMultiple,
                   'is_comfortable_self_learning': forms.RadioSelect,
                   'is_classroom_better': forms.RadioSelect,
                   'is_student_expectations': forms.RadioSelect,
                   'is_help_get_interview': forms.RadioSelect,
                   'is_help_get_job': forms.RadioSelect,
                   'is_got_job': forms.RadioSelect,
                   'relevance': forms.RadioSelect,
                   'information_content': forms.RadioSelect,
                   'audio_video_quality': forms.RadioSelect,
                   'presentation_quality': forms.RadioSelect,
                   'overall_rating': forms.RadioSelect,
                   'testimonial': forms.Textarea,
                   'any_other_suggestions': forms.Textarea}


class LatexWorkshopFileUploadForm(forms.ModelForm):

    class Meta:
        model = LatexWorkshopFileUpload
        fields = '__all__'


class MapCourseWithFossForm(forms.ModelForm):
    """Loading only the foss which is AvailableForWorkshop

    To display new foss need to make one entry with default language english
    in FossAvailableForWorkshop.
    """
    foss = forms.ModelChoiceField(
        queryset=FossCategory.objects.filter(
            id__in=FossAvailableForWorkshop.objects.filter(status=1).values('foss').distinct(),
            status=True
        )
    )

    class Meta:
        model = CourseMap
        exclude = ()
