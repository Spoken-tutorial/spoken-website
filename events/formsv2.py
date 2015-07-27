from django import forms
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from events.models import *
from datetime import datetime, date
from events.helpers import get_academic_years


class StudentBatchForm(forms.ModelForm):
  year = forms.ChoiceField(choices = get_academic_years())
  csv_file = forms.FileField(required = True)
  class Meta:
    model = StudentBatch
    exclude = ['academic', 'stcount', 'organiser']

class NewStudentBatchForm(forms.ModelForm):
  csv_file = forms.FileField(required = True)

  class Meta:
    model = StudentBatch
    exclude = ['academic', 'year', 'department', 'stcount', 'organiser']

class UpdateStudentBatchForm(forms.ModelForm):
  year = forms.ChoiceField(choices = get_academic_years())
  class Meta:
    model = StudentBatch
    exclude = ['academic', 'stcount', 'organiser']

class TrainingRequestForm(forms.ModelForm):
  department = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.none())
  course_type = forms.ChoiceField(choices=[('', '---------'), (0, 'Software Course outside lab hours'), (1, 'Software Course mapped in lab hours'), (2, ' Software Course unmapped in lab hours')])
  course = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.none())
  batch = forms.ModelChoiceField(empty_label='---------', queryset=StudentBatch.objects.none())
  training_planner = forms.CharField()
  class Meta:
    model = TrainingRequest
    exclude = ['participants', 'status', 'training_planner']

  def clean(self):
    if self.cleaned_data:
      tp = TrainingPlanner.objects.get(pk=self.cleaned_data['training_planner'])
      if 'department' in self.cleaned_data and self.cleaned_data['department'] \
        and 'batch' in self.cleaned_data and self.cleaned_data['batch']:
        if tp.is_full(self.cleaned_data['department'], self.cleaned_data['batch']):
          raise forms.ValidationError("No. of training requests for this department exceeded.")

        if 'course_type' in self.cleaned_data and self.cleaned_data['course_type']:
          if tp.is_course_full(self.cleaned_data['course_type'], self.cleaned_data['department'], self.cleaned_data['batch']):
            raise forms.ValidationError("No. of training requests for selected course type exceeded")
      
      # Date restriction
      if self.cleaned_data and 'sem_start_date' in self.cleaned_data and self.cleaned_data['sem_start_date']:
        start_date, end_date =tp.get_current_semester_date_duration_new()
        print tp.id, '-------------------'
        print start_date, end_date, self.cleaned_data['sem_start_date']
        if not (self.cleaned_data['sem_start_date'] <= end_date and self.cleaned_data['sem_start_date'] >= start_date):
          raise forms.ValidationError("Invalid semester start date")
    return self.cleaned_data
  
  def __init__(self, *args, **kwargs):
    user = kwargs.pop('user')
    super(TrainingRequestForm, self).__init__(*args, **kwargs)
    
    if kwargs and 'data' in kwargs:
      # Generating course list based on course type
      if 'course_type' in kwargs['data'] and kwargs['data']['course_type'] != '':
        courses = CourseMap.objects.filter(category=kwargs['data']['course_type'])
        choices = [('', '---------'),]
        for course in courses:
          choices.append((course.id, course.course_name()))
        self.fields['course'].queryset = CourseMap.objects.filter(category=kwargs['data']['course_type'])
        self.fields['course'].choices = choices
        self.fields['course'].initial = kwargs['data']['course']
      # Generating students batch list based on department
      if kwargs['data']['department'] != '':
        department = kwargs['data']['department']
        self.fields['batch'].queryset = StudentBatch.objects.filter(academic_id=user.organiser.academic.id, stcount__gt=0, department_id=department)
        self.fields['batch'].initial =  kwargs['data']['batch']
    # overwrite department choices
    self.fields['department'].queryset = Department.objects.filter(id__in=StudentBatch.objects.filter(academic=user.organiser.academic, stcount__gt=0).values_list('department_id'))

class TrainingRequestEditForm(forms.ModelForm):
  course_type = forms.ChoiceField(choices=[('', '---------'), (0, 'Software Course outside lab hours'), (1, 'Software Course mapped in lab hours'), (2, ' Software Course unmapped in lab hours')])
  course = forms.ModelChoiceField(empty_label='---------', queryset=CourseMap.objects.none())
  training_planner = forms.CharField()
  class Meta:
    model = TrainingRequest
    exclude = ['participants', 'status', 'training_planner', 'department', 'batch']
  
  def clean(self):
    # Date restriction
    if self.cleaned_data and 'sem_start_date' in self.cleaned_data and self.cleaned_data['sem_start_date']:
      tp = TrainingPlanner.objects.get(pk=self.cleaned_data['training_planner'])
      start_date, end_date =tp.get_current_semester_date_duration_new()
      print start_date, end_date, self.cleaned_data['sem_start_date']
      if not (self.cleaned_data['sem_start_date'] <= end_date and self.cleaned_data['sem_start_date'] >= start_date):
        raise forms.ValidationError("Invalid semester start date")
    return self.cleaned_data

  def __init__(self, *args, **kwargs):
    training = kwargs.pop('training', None)
    user = kwargs.pop('user', None)
    super(TrainingRequestEditForm, self).__init__(*args, **kwargs)
    flag = True
    data = kwargs.pop('data', None)
    if data and 'course_type' in data:
      if data['course_type']:
        print 1
        self.fields['course'].queryset = CourseMap.objects.filter(category=data['course_type'])
        if 'course' in data and data['course']:
          self.fields['course'].initial = data['course']
      else:
        print 2
        flag = False
    else:
      print 3
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
  category = forms.ChoiceField(choices=[('', '---------'), (1, 'Software Course mapped in lab hours'), (2, ' Software Course unmapped in lab hours')])
  course = forms.ModelChoiceField(queryset=LabCourse.objects.all())
  foss = forms.ModelChoiceField(queryset=FossCategory.objects.filter(status=True))
  class Meta:
    model = CourseMap
    exclude = ['test']

  def __init__(self, *args, **kwargs):
    super(CourseMapForm, self).__init__(*args, **kwargs)

class SingleTrainingForm(forms.ModelForm):
  training_type = forms.ChoiceField(choices=[('', '---------'), (0, 'School'),(1,'Vocational'),(2,'Live workshop'),(3,'Pilot workshop')])
  csv_file = forms.FileField(required = True)
  class Meta:
    model = SingleTraining
    exclude = ['academic', 'organiser', 'status', 'participant_count']
  
  def clean(self): 
        #self.cleaned_data['csv_file']
    if self.cleaned_data['csv_file'].name.split('.')[-1] == 'csv':
      pass
    else:
        raise forms.ValidationError("Invalid file format.")
    return self.cleaned_data
    
  def clean_tdate(self):
    today = datetime.now()
    tdate = self.cleaned_data['tdate']
    if today.date() > tdate:
      raise forms.ValidationError("Invalid semester training date")
    return tdate
