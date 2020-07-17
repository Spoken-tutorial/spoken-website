
from builtins import object
import datetime as dt

from django import forms

from events.models import *
from events.helpers import get_academic_years
from cms.validators import validate_csv_file

class StudentBatchForm(forms.ModelForm):
  year = forms.ChoiceField(choices = get_academic_years())
  csv_file = forms.FileField(required = True)
  department = forms.ModelChoiceField(
        queryset = Department.objects.filter(~Q(name='others'))
  )

  class Meta(object):
    model = StudentBatch
    exclude = ['academic', 'stcount', 'organiser', 'batch_name']
  
  def clean_csv_file(self):
    data = self.cleaned_data["csv_file"]
    file_data = validate_csv_file(data)
    return file_data

class NewStudentBatchForm(forms.ModelForm):
  csv_file = forms.FileField(required = True)

  class Meta(object):
    model = StudentBatch
    exclude = ['academic', 'year', 'department', 'stcount', 'organiser', 'batch_name']
  
  def clean_csv_file(self):
    data = self.cleaned_data["csv_file"]
    file_data = validate_csv_file(data)
    return file_data

class UpdateStudentBatchForm(forms.ModelForm):
  year = forms.ChoiceField(choices = get_academic_years())
  department = forms.ModelChoiceField(
        queryset = Department.objects.filter(~Q(name='others'))
  )
  class Meta(object):
    model = StudentBatch
    exclude = ['academic', 'stcount', 'organiser','batch_name']

class UpdateStudentYearBatchForm(forms.ModelForm):
  year = forms.ChoiceField(choices = get_academic_years())
  class Meta(object):
    model = StudentBatch
    exclude = ['academic', 'stcount', 'organiser','department','batch_name']

class TrainingRequestForm(forms.ModelForm):
  department = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.none())
  course_type = forms.ChoiceField(choices=[('', '---------'), (0, 'Software Course outside lab hours'), (1, 'Software Course mapped in lab hours'), (2, ' Software Course unmapped in lab hours')])
  foss_category = forms.ChoiceField(choices=[('', '---------'), (0, 'Foss available only for Training'), (1, 'Foss available for Training and Test')])
  course = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.filter(category=0))
  batch = forms.ModelChoiceField(empty_label='---------', queryset=StudentBatch.objects.none())
  training_planner = forms.CharField()
  class Meta(object):
    model = TrainingRequest
    exclude = ['participants', 'status', 'training_planner', 'cert_status']

  def clean(self):
    if self.cleaned_data:
      #48hrs, batch id fetched
      batch_id_list = []
      sm_batch_all = StudentMaster.objects.all()
      for i in sm_batch_all:
        if dt.datetime.today().isoformat() < (i.created + dt.timedelta(days=2)).isoformat():
          batch_id_list.append(i.batch_id)
      batch_id_set = set(batch_id_list)
      uniq_batch_id = []
      for j in batch_id_set:
        uniq_batch_id.append(j)
      tp = TrainingPlanner.objects.get(pk=self.cleaned_data['training_planner'])

      # Date restriction
      if self.cleaned_data and 'sem_start_date' in self.cleaned_data and self.cleaned_data['sem_start_date']:
        start_date, end_date =tp.get_current_semester_date_duration_new()
        print((start_date, end_date, self.cleaned_data['sem_start_date']))
        if not (self.cleaned_data['sem_start_date'] <= end_date and self.cleaned_data['sem_start_date'] >= start_date):
          raise forms.ValidationError("Invalid semester start date")


      if self.cleaned_data and 'training_start_date' in self.cleaned_data and self.cleaned_data['training_start_date']:
        start_date, end_date =tp.get_current_semester_date_duration()
        print((start_date, end_date, self.cleaned_data['sem_start_date']))
        if not (self.cleaned_data['training_start_date'] <= end_date and self.cleaned_data['training_start_date'] >= start_date):
          raise forms.ValidationError("Invalid training start date")

      if self.cleaned_data and 'training_end_date' in self.cleaned_data and self.cleaned_data['training_end_date']:
        start_date, end_date =tp.get_current_semester_date_duration()
        print((start_date, end_date, self.cleaned_data['training_end_date']))
        if not (self.cleaned_data['training_end_date'] <= end_date and self.cleaned_data['training_end_date'] >= start_date):
          raise forms.ValidationError("Invalid training end date")


    return self.cleaned_data

  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    course_type = kwargs.pop('course_type')
    super(TrainingRequestForm, self).__init__(*args, **kwargs)
    self.fields['course_type'].choices = course_type


    if kwargs and 'data' in kwargs:
      # Generating students batch list based on department
      if kwargs['data']['department'] != '':
        department = kwargs['data']['department']
        self.fields['batch'].queryset = StudentBatch.objects.filter(academic_id=user.organiser.academic.id, stcount__gt=0, department_id=department)
        self.fields['batch'].initial =  kwargs['data']['batch']
    # overwrite department choices
    self.fields['department'].queryset = Department.objects.filter(id__in=StudentBatch.objects.filter(academic=user.organiser.academic, stcount__gt=0).values_list('department_id'))

class TrainingRequestEditForm(forms.ModelForm):
  course_type = forms.ChoiceField(choices=[('', '---------'), (0, 'Software Course outside lab hours'), (1, 'Software Course mapped in lab hours'), (2, ' Software Course unmapped in lab hours')])
  training_planner = forms.CharField()
  department = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.none())
  batch = forms.ModelChoiceField(empty_label='---------', queryset=StudentBatch.objects.none())
  foss_category = forms.ChoiceField(choices=[('', '---------'), (0, 'Foss available only for Training'), (1, 'Foss available for Training and Test')])
  course = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.filter(category=0))
  class Meta(object):
    model = TrainingRequest
    exclude = ['participants', 'status', 'training_planner', 'cert_status']

  def clean(self):
    # Date restriction
    if self.cleaned_data and 'sem_start_date' in self.cleaned_data and self.cleaned_data['sem_start_date']:
      tp = TrainingPlanner.objects.get(pk=self.cleaned_data['training_planner'])
      start_date, end_date =tp.get_current_semester_date_duration_new()
      if not (self.cleaned_data['sem_start_date'] <= end_date and self.cleaned_data['sem_start_date'] >= start_date):
        raise forms.ValidationError("Invalid semester start date")

    if self.cleaned_data and 'training_start_date' in self.cleaned_data and self.cleaned_data['training_start_date']:
      tp = TrainingPlanner.objects.get(pk=self.cleaned_data['training_planner'])
      start_date, end_date =tp.get_current_semester_date_duration()
      if not (self.cleaned_data['training_start_date'] <= end_date and self.cleaned_data['training_start_date'] >= start_date):
        raise forms.ValidationError("Invalid training start date")

    if self.cleaned_data and 'training_end_date' in self.cleaned_data and self.cleaned_data['training_end_date']:
      tp = TrainingPlanner.objects.get(pk=self.cleaned_data['training_planner'])
      start_date, end_date =tp.get_current_semester_date_duration()
      if not (self.cleaned_data['training_end_date'] <= end_date and self.cleaned_data['training_end_date'] >= start_date):
        raise forms.ValidationError("Invalid training end date")
    return self.cleaned_data

  def __init__(self, *args, **kwargs):
    training = kwargs.pop('training', None)
    user = kwargs.pop('user', None)
    super(TrainingRequestEditForm, self).__init__(*args, **kwargs)
    flag = True
    data = kwargs.pop('data', None)

    if not flag and training:
      self.fields['course_type'].initial = training.course_type
      self.fields['course'].queryset = CourseMap.objects.filter(category=0)
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
      self.fields['training_start_date'].initial = training.training_start_date
      self.fields['training_end_date'].initial = training.training_end_date

    self.fields['course_type'].initial = training.course_type
    self.fields['course'].initial = training.course_id
    #department
    self.fields['department'].queryset = Department.objects.filter(id__in=StudentBatch.objects.filter(academic=user.organiser.academic, stcount__gt=0).values_list('department_id'))
    self.fields['department'].initial = training.department

    #overwrite choice
    self.fields['batch'].queryset = StudentBatch.objects.filter(
      academic_id=user.organiser.academic.id,
      stcount__gt=0,
      department_id=training.department.id
    )
    self.fields['batch'].initial = training.batch

    # update form choice when check is_valid
    if data and 'department' in data:
        self.fields['batch'].queryset = StudentBatch.objects.filter(
          academic_id=user.organiser.academic.id,
          stcount__gt=0,
          department_id=data['department']
        )

class CourseMapForm(forms.ModelForm):
  category = forms.ChoiceField(choices=[('', '---------'), (1, 'Software Course mapped in lab hours'), (2, ' Software Course unmapped in lab hours')])
  course = forms.ModelChoiceField(queryset=LabCourse.objects.all())
  foss = forms.ModelChoiceField(
        queryset = FossCategory.objects.filter(
            id__in=FossAvailableForWorkshop.objects.filter(status=1).values('foss').distinct(),
            status=True
        )
  )

  class Meta(object):
    model = CourseMap
    exclude = ['test']

  def __init__(self, *args, **kwargs):
    super(CourseMapForm, self).__init__(*args, **kwargs)

class UserForm(forms.ModelForm):
  gender = forms.ChoiceField(choices=[('Male', 'Male'),('Female','Female')])
  class Meta(object):
    model = User
    exclude = ['password','last_login','is_superuser','username','is_staff','is_active','date_joined','groups','user_permissions']

  # def clean_email(self):
  #   email = self.cleaned_data['email']
  #   try:
  #     if not validate_email(email):
  #       raise forms.ValidationError(u'%s is not valid email.' % email )
  #   except:
  #     raise forms.ValidationError(u'%s is not valid email.' % email )

  def __init__(self, *args, **kwargs):
    super(UserForm, self).__init__(*args, **kwargs)
    if 'instance' in kwargs:
      self.fields['gender'].initial = kwargs['instance'].student.gender


class SingleTrainingForm(forms.ModelForm):
  training_type = forms.ChoiceField(choices=[('', '---------'), (0, 'School'),(3,'Vocational'),(1,'Live workshop'),(2,'Pilot workshop')])
  csv_file = forms.FileField(required = True)
  class Meta(object):
    model = SingleTraining
    exclude = ['organiser', 'status', 'participant_count', 'total_participant_count']

  def __init__(self, *args, **kwargs):
    super(SingleTrainingForm, self).__init__(*args, **kwargs)
    self.fields['academic'].required = False
    self.fields['state'].required = False
    self.fields['institution_type'].required = False

  def clean(self):
        #self.cleaned_data['csv_file']
    if self.cleaned_data['csv_file'].name.split('.')[-1] == 'csv':
      pass
    else:
        raise forms.ValidationError("Invalid file format.")
    return self.cleaned_data

  def clean_tdate(self):
    today = dt.datetime.now()
    tdate = self.cleaned_data['tdate']
    if today.date() > tdate:
      raise forms.ValidationError("Invalid semester training date")
    return tdate

class SingleTrainingEditForm(forms.ModelForm):
  training_type = forms.ChoiceField(choices=[('', '---------'), (0, 'School'),(3,'Vocational'),(1,'Live workshop'),(2,'Pilot workshop')])
  csv_file = forms.FileField(required = False)
  class Meta(object):
    model = SingleTraining
    exclude = ['organiser', 'status', 'participant_count', 'total_participant_count']

  def __init__(self, *args, **kwargs):
    super(SingleTrainingEditForm, self).__init__(*args, **kwargs)
    self.fields['academic'].required = False
    self.fields['state'].required = False
    self.fields['institution_type'].required = False

  def clean(self):
        #self.cleaned_data['csv_file']
    if 'csv_file' in self.cleaned_data and self.cleaned_data['csv_file']:
      if self.cleaned_data['csv_file'].name.split('.')[-1] == 'csv':
        pass
      else:
        raise forms.ValidationError("Invalid file format.")
    return self.cleaned_data

  def clean_tdate(self):
    today = dt.datetime.now()
    tdate = self.cleaned_data['tdate']
    if today.date() > tdate:
      raise forms.ValidationError("Invalid semester training date")
    return tdate


class OrganiserFeedbackForm(forms.ModelForm):
  offered_training_foss = forms.ModelMultipleChoiceField(
    # queryset=FossCategory.objects.filter(status=1), 
    queryset=FossCategory.objects.filter(
      id__in=CourseMap.objects.filter(
          category=0    #removed test condition
        ).values_list(
          'foss_id'
        )
      ),
    widget=forms.CheckboxSelectMultiple)
  trained_foss = forms.ModelMultipleChoiceField(
    # queryset=FossCategory.objects.filter(status=1), 
    queryset=FossCategory.objects.filter(
      id__in=CourseMap.objects.filter(
          category=0    #removed test condition
        ).values_list(
          'foss_id'
        )
      ),
    widget=forms.CheckboxSelectMultiple)
  class Meta(object):
    model = OrganiserFeedback
    fields = '__all__'
    widgets = {'student_stream': forms.CheckboxSelectMultiple,
              'language' : forms.CheckboxSelectMultiple,
              'trained_foss' : forms.CheckboxSelectMultiple,
              'helpful_for' : forms.CheckboxSelectMultiple ,
              'is_comfortable_self_learning' : forms.RadioSelect ,
              'is_classroom_better' : forms.RadioSelect ,
              'is_student_expectations' : forms.RadioSelect ,
              'is_help_get_interview' : forms.RadioSelect ,
              'is_help_get_job' : forms.RadioSelect ,
              'is_got_job' : forms.RadioSelect ,
              'relevance' : forms.RadioSelect,
              'information_content' : forms.RadioSelect,
              'audio_video_quality' : forms.RadioSelect,
              'presentation_quality' : forms.RadioSelect ,
              'overall_rating' : forms.RadioSelect ,
              'testimonial' : forms.Textarea ,
              'any_other_suggestions' : forms.Textarea}

class LatexWorkshopFileUploadForm(forms.ModelForm):
  class Meta(object):
    model = LatexWorkshopFileUpload
    fields = '__all__'


class MapCourseWithFossForm(forms.ModelForm):
    # Loading only the foss which is AvailableForWorkshop
    # To display new foss need to make one entry with default language english \
    # in FossAvailableForWorkshop.
    foss = forms.ModelChoiceField(
        queryset = FossCategory.objects.filter(
            id__in=FossAvailableForWorkshop.objects.filter(status=1).values('foss').distinct(),
            status = True
        )
    )
    class Meta(object):
        model = CourseMap
        exclude = ()

class STWorkshopFeedbackForm(forms.ModelForm):
  class Meta(object):
    model = STWorkshopFeedback
    fields = '__all__'
    widgets = {
              'acquired_knowledge' : forms.RadioSelect ,
              'suff_instruction' : forms.RadioSelect ,
              'diff_instruction' : forms.RadioSelect ,
              'method_easy' : forms.RadioSelect ,
              'time_sufficient' : forms.RadioSelect ,
              'desired_objective': forms.RadioSelect ,
              'recommend' : forms.RadioSelect ,
              'like_to_part' : forms.RadioSelect,
              'side_by_side_effective' : forms.RadioSelect,
              'dont_like_self_learning_method' : forms.RadioSelect,

              'not_self_explanatory' : forms.RadioSelect,
              'logical_sequence' : forms.RadioSelect ,
              'examples_help' : forms.RadioSelect ,
              'instructions_easy_to_follow' : forms.RadioSelect ,
              'difficult_instructions_in_tutorial' : forms.RadioSelect ,
              'translate' : forms.RadioSelect ,

              'useful_learning' : forms.RadioSelect ,
              'help_improve_performance' : forms.RadioSelect ,
              'plan_to_use_future' : forms.RadioSelect ,
              'confident_to_apply_knowledge' : forms.RadioSelect ,
              'difficult_simultaneously' : forms.RadioSelect ,
              'too_fast' : forms.RadioSelect ,
              'too_slow' : forms.RadioSelect ,
              'interface_comfortable' : forms.RadioSelect ,
              'satisfied' : forms.RadioSelect ,
              'self_learning_intrest' : forms.RadioSelect ,
              'language_diff_to_understand' : forms.RadioSelect ,
              'not_like_method_forums' : forms.RadioSelect ,
              'forum_helpful' : forms.RadioSelect ,
              'owing_to_forums' : forms.RadioSelect ,

              'ws_quality' : forms.RadioSelect ,
              'overall_content_quality' : forms.RadioSelect ,
              'clarity_of_explanation' : forms.RadioSelect ,
              'flow' : forms.RadioSelect ,
              'relevance' : forms.RadioSelect ,
              'guidelines' : forms.RadioSelect ,
              'overall_video_quality' : forms.RadioSelect ,
              'text_readability' : forms.RadioSelect ,
              'clarity_of_speech' : forms.RadioSelect ,
              'visual_presentation' : forms.RadioSelect ,
              'pace_of_tutorial' : forms.RadioSelect ,
              'time_management' : forms.RadioSelect ,
              'experience_of_learning' : forms.RadioSelect ,
              'overall_arrangement' : forms.RadioSelect ,
              'like_abt_ws' : forms.Textarea ,
              'how_make_better' : forms.Textarea,
              'experience' : forms.Textarea ,
              'suggestions' : forms.Textarea,
              'training_any_comment' : forms.Textarea,
              'content_any_comment' : forms.Textarea,
              'learning_any_comment': forms.Textarea,
              }
  def __init__(self, *args, **kwargs):
    super(STWorkshopFeedbackForm, self).__init__(*args, **kwargs)
    self.fields['like_abt_ws'].required = False
    self.fields['how_make_better'].required = False
    self.fields['experience'].required = False
    self.fields['suggestions'].required = False
    self.fields['name'].required = False
    self.fields['email'].required = False
    self.fields['training_any_comment'].required = False
    self.fields['content_any_comment'].required = False
    self.fields['learning_any_comment'].required = False

class STWorkshopFeedbackFormPre(forms.ModelForm):
  class Meta(object):
    model = STWorkshopFeedbackPre
    fields = '__all__'
    exclude = ['user']
    widgets = {
              'content_management' : forms.RadioSelect ,
              'configuration_management' : forms.RadioSelect ,
              'creating_basic_content' : forms.RadioSelect ,
              'edit_existing_content' : forms.RadioSelect ,
              'create_new_content' : forms.RadioSelect ,
              'grp_entity_ref' : forms.RadioSelect ,
              'taxonomy' : forms.RadioSelect ,
              'managing_content' : forms.RadioSelect ,
              'creating_dummy_content' : forms.RadioSelect ,
              'modify_display_content' : forms.RadioSelect ,
              'contents_using_view' : forms.RadioSelect ,
              'table_of_fields_with_views' : forms.RadioSelect ,
              'control_display_images' : forms.RadioSelect ,
              'adding_func' : forms.RadioSelect ,
              'finding_modules' : forms.RadioSelect ,
              'modifying_page_layout' : forms.RadioSelect ,
              'menu_endpoints' : forms.RadioSelect ,
              'styling_using_themes' : forms.RadioSelect ,
              'installig_ad_themes' : forms.RadioSelect ,
              'people_management' : forms.RadioSelect ,
              'site_management' : forms.RadioSelect ,

              }


class STWorkshopFeedbackFormPost(forms.ModelForm):
  class Meta(object):
    model = STWorkshopFeedbackPost
    fields = '__all__'
    exclude = ['user']
    widgets = {
              'spfriendly' : forms.RadioSelect ,
              'diff_watch_practice' : forms.RadioSelect ,
              'satisfied_with_learning_experience' : forms.RadioSelect ,
              'confident' : forms.RadioSelect ,
              'side_by_side_hold_intrest' : forms.RadioSelect ,
              'ws_not_useful' : forms.RadioSelect ,
              'can_learn_other' : forms.RadioSelect ,
              'wantto_conduct_incollege' : forms.RadioSelect ,
              'esy_to_conduct_own' : forms.RadioSelect ,
              'ask_student_to_use' : forms.RadioSelect ,
              'possible_to_use_therotical' : forms.RadioSelect ,
              'not_self_explanatory' : forms.RadioSelect ,
              'logical_sequence' : forms.RadioSelect ,
              'examples_help' : forms.RadioSelect ,
              'other_language' : forms.RadioSelect ,
              'instructions_easy_to_follow' : forms.RadioSelect ,
              'language_complicated' : forms.RadioSelect ,
              'acquired_knowledge' : forms.RadioSelect ,
              'suff_instruction_by_prof' : forms.RadioSelect ,
              'suff_instruction_by_staff' : forms.RadioSelect ,
              'method_easy' : forms.RadioSelect ,
              'desired_objective' : forms.RadioSelect ,
              'recommend' : forms.RadioSelect ,
              'like_to_part' : forms.RadioSelect ,
              'learn_other_side_by_side' : forms.RadioSelect ,
              'referred_forums' : forms.RadioSelect ,
              'referred_forums_after' : forms.RadioSelect ,
              'asked_ques_forums' : forms.RadioSelect ,
              'not_answer_doubts' : forms.RadioSelect ,
              'forum_helpful' : forms.RadioSelect ,
              'doubts_solved_fast' : forms.RadioSelect ,
              'need_not_post' : forms.RadioSelect ,
              'faster_on_forums' : forms.RadioSelect ,
              'not_have_to_wait' : forms.RadioSelect ,
              'not_like_method_forums' : forms.RadioSelect ,
              'helpful_pre_ans_ques' : forms.RadioSelect ,
              'not_like_reveal_identity' : forms.RadioSelect ,
              'forum_motivated' : forms.RadioSelect ,
              'per_asked_ques_before_tuts' : forms.RadioSelect ,
              'content_management' : forms.RadioSelect ,
              'configuration_management' : forms.RadioSelect ,
              'creating_basic_content' : forms.RadioSelect ,
              'edit_existing_content' : forms.RadioSelect ,
              'create_new_content' : forms.RadioSelect ,
              'grp_entity_ref' : forms.RadioSelect ,
              'taxonomy' : forms.RadioSelect ,
              'managing_content' : forms.RadioSelect ,
              'creating_dummy_content' : forms.RadioSelect ,
              'modify_display_content' : forms.RadioSelect ,
              'contents_using_view' : forms.RadioSelect ,
              'table_of_fields_with_views' : forms.RadioSelect ,
              'control_display_images' : forms.RadioSelect ,
              'adding_func' : forms.RadioSelect ,
              'finding_modules' : forms.RadioSelect ,
              'modifying_page_layout' : forms.RadioSelect ,
              'menu_endpoints' : forms.RadioSelect ,
              'styling_using_themes' : forms.RadioSelect ,
              'installig_ad_themes' : forms.RadioSelect ,
              'people_management' : forms.RadioSelect ,
              'site_management' : forms.RadioSelect ,
              'ws_quality' : forms.RadioSelect ,
              'relevance' : forms.RadioSelect ,
              'guidelines' : forms.RadioSelect ,
              'overall_video_quality' : forms.RadioSelect ,
              'text_readability' : forms.RadioSelect ,
              'clarity_of_speech' : forms.RadioSelect ,
              'visual_presentation' : forms.RadioSelect ,
              'pace_of_tutorial' : forms.RadioSelect ,
              'arrangement' : forms.RadioSelect ,
              'network' : forms.RadioSelect ,
              'installation_help' : forms.RadioSelect ,
              'time_for_handson' : forms.RadioSelect ,
              'experience_of_learning' : forms.RadioSelect ,
              'overall_arrangement' : forms.RadioSelect ,
              'like_to_create_st_details' : forms.Textarea ,
              'foss_where' : forms.Textarea ,
              'explain' : forms.Textarea ,
              'purpose_of_attending' : forms.Textarea ,
              'like_abt_ws' : forms.Textarea ,
              'how_make_better' : forms.Textarea,
              'experience' : forms.Textarea ,
              'suggestions' : forms.Textarea,
              }

class LearnDrupalFeedbackForm(forms.ModelForm):
  class Meta(object):
    model = LearnDrupalFeedback
    fields = '__all__'
    widgets = {
              'feedback' : forms.Textarea,
              }

  def __init__(self, *args, **kwargs):
    super(LearnDrupalFeedbackForm, self).__init__(*args, **kwargs)
    self.fields['name'].required = False
    self.fields['phonemob'].required = False
    self.fields['affiliation'].required = False
    self.fields['place'].required = False
    self.fields['agegroup'].required = False
    self.fields['currentstatus_other'].required = False
    self.fields['is_drupal_in_curriculum'].required = False
    self.fields['need_help_in_organizing'].required = False
    self.fields['when_plan_to_conduct'].required = False
    self.fields['did_undergo_st_training'].required = False
    self.fields['rate_spoken'].required = False
    self.fields['useful_for_placement_for_students'].required = False
    self.fields['useful_for_placement'].required = False
    self.fields['like_to_learn_other_foss'].required = False
    self.fields['mention_foss'].required = False
    self.fields['like_to_give_testimonial'].required = False
    self.fields['testimonial'].required = False
      
class TrainingManagerForm(forms.Form):
    state = forms.ChoiceField(choices=[('', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    college = forms.ChoiceField(choices=[('0', '-- None --'), ], widget=forms.Select(attrs = {}), required = False)
    choices = forms.ChoiceField(choices=[('', '-- None --'), ('S', 'Successfull'), ('F', 'Failed'),('O','Ongoing'),('R','Reconciled')])
    fdate = forms.DateTimeField(required = False)
    tdate = forms.DateTimeField(required = False)

    def __init__(self, user,*args, **kwargs):
        initial = ''
        if 'instance' in kwargs:
            initial = kwargs["instance"]
            del kwargs["instance"]

        if 'user' in kwargs:
            user = kwargs["user"]
            del kwargs["user"]

        super(TrainingManagerForm, self).__init__(*args, **kwargs)
        

        rp_states = ResourcePerson.objects.filter(status=1,user=user)
        # load the choices
        state_list = list(State.objects.filter(id__in=rp_states.values('state')).order_by('name').values_list('id', 'name'))
        state_list.insert(0, ('', '-- None --'))
        self.fields['state'].choices = state_list
        centre_choices =[]
        centre_choices.insert(0,(0,'All Colleges'))
        
        if args:
            if 'state' in args[0]:
                if args[0]['state'] and args[0]['state'] != '' and args[0]['state'] != 'None':
                    centre_qs = AcademicCenter.objects.filter(state_id=args[0]['state']).order_by('institution_name')
                    centre_choices = [(x.id, '%s, %s' % (x.institution_name, x.academic_code)) for x in centre_qs]
                    centre_choices.insert(0,(0,'All Colleges'))
                    self.fields['college'].choices = centre_choices
                    self.fields['college'].widget.attrs = {}
        # if initial:
        #     self.fields['state'].initial = initial.academic.state_id
        #     centre_qs = AcademicCenter.objects.filter(district_id=initial.academic.district_id)
        #     centre_choices = [(x.id, '%s, %s' % (x.institution_name, x.academic_code)) for x in centre_qs]
        #     centre_choices.insert(0,(0,'All Colleges'))
        #     self.fields['college'].choices = centre_choices

        #     # initial data
        #     self.fields['college'].initial = initial.academic_id

ACTIVATION_STATUS = (
    (None, "--------"),
    (1, "Active"),
    (3, "Deactive"))

class DateInput(forms.DateInput):
    input_type = 'date'

class StudentGradeFilterForm(forms.Form):
  foss = forms.ModelMultipleChoiceField(queryset=FossCategory.objects.all())
  state = forms.ModelMultipleChoiceField(queryset=State.objects.all(), required=False)
  city = forms.ModelMultipleChoiceField(queryset=City.objects.all().order_by('name'), required=False)
  grade = forms.IntegerField(min_value=0, max_value=100)
  institution_type = forms.ModelMultipleChoiceField(queryset=InstituteType.objects.all(), required=False)
  activation_status = forms.ChoiceField(choices = ACTIVATION_STATUS, required=False)
  from_date = forms.DateField(widget=DateInput(), required=False)
  to_date = forms.DateField(widget=DateInput(), required=False)

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['foss'].widget.attrs.update({'class': 'form-control'})
    self.fields['state'].widget.attrs.update({'class': 'form-control'})
    self.fields['grade'].widget.attrs.update({'class': 'form-control'})
    self.fields['institution_type'].widget.attrs.update({'class': 'form-control'})
    self.fields['activation_status'].widget.attrs.update({'class': 'form-control'})
    self.fields['from_date'].widget.attrs.update({'class': 'form-control'})
    self.fields['to_date'].widget.attrs.update({'class': 'form-control'})