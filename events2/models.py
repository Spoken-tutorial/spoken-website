from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from datetime import datetime, date
from django.db.models.signals import pre_delete

from creation.models import FossCategory, Language, FossAvailableForWorkshop
from events.models import AcademicCenter, Department, AcademicCenter, Organiser


# Create your models here.
class Student(models.Model):
  user = models.OneToOneField(User)
  gender = models.CharField(max_length = 15)
  verified = models.BooleanField(default=False)
  error = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __unicode__(self):
    return self.user.first_name
  
  def student_fullname(self):
    if self.user.first_name:
      return '%s %s' % (self.user.first_name, self.user.last_name)
    return self.user.username

  def is_student_has_attendance(self):
    if TrainingAttend.objects.filter(student_id=self.id).exists():
      return True
    return False

class StudentBatch(models.Model):
  academic = models.ForeignKey(AcademicCenter)
  organiser = models.ForeignKey(Organiser)
  department = models.ForeignKey(Department)
  year = models.PositiveIntegerField() # 2010-2014
  stcount = models.PositiveIntegerField(default=0)

  class Meta:
    unique_together = ("academic", "year", "department")

  def __unicode__(self):
    return '%s, %s Batch' % (self.department.name, self.year)
  
  def get_batch_info(self):
    return '%s, %s, %s Batch' % (self.academic, self.department.name, self.year)

  def student_count(self):
    return StudentMaster.objects.filter(batch_id = self.id).count()

  def can_add_student(self, organiser_id):
    if self.organiser.id == organiser_id:
      return True
    return False

  def update_student_count(self):
    self.stcount = StudentMaster.objects.filter(batch_id = self.id).count()
    self.save()
    return self.stcount
  
  def is_foss_batch_acceptable(self, course_id):
    sm = StudentMaster.objects.filter(batch_id=self.id)
    for s in sm:
      if not TrainingAttend.objects.filter(student_id=s.student_id, training__course_id=course_id).exists():
       return True
    return False

class StudentMaster(models.Model):
  batch = models.ForeignKey(StudentBatch)
  student = models.ForeignKey(Student)
  moved = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  class Meta:
    unique_together = ("batch", "student")


class Semester(models.Model):
  name = models.CharField(max_length = 50)
  even = models.BooleanField(default = True)

  def __unicode__(self):
    return self.name


class LabCourse(models.Model):
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __unicode__(self):
    return self.name


class CourseMap(models.Model):
  #name = models.CharField(max_length=200, null=True, blank=True)
  course = models.ForeignKey(LabCourse, null=True, blank=True)
  foss = models.ForeignKey(FossCategory)
  test = models.BooleanField(default=False)
  # {0 => one day workshop, 1 => mapped course, 2 => unmapped course}
  category = models.PositiveIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __unicode__(self):
    if self.course_id:
      return '%s (%s)' % (self.foss.foss, self.course.name)
    return self.foss.foss

  def course_name(self):
    if self.course_id:
      return '%s - %s' % (self.course.name, self.foss.foss)
    return self.foss

  class Meta:
    unique_together = ("course", "foss", "category")
    ordering = ('foss',)


class TrainingPlanner(models.Model):
  year = models.CharField(max_length = 50)
  academic = models.ForeignKey(AcademicCenter)
  organiser = models.ForeignKey(Organiser)
  semester = models.ForeignKey(Semester)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  #created = models.DateTimeField()
  #updated = models.DateTimeField()

  def __unicode__(self):
    return self.semester.name

  def training_requests(self):
    return TrainingRequest.objects.filter(training_planner_id = self.id)

  def get_semester(self):
    if self.semester.even:
      return 'January - June, %s' % (int(self.year) + 1)
    return 'July - December, %s' % (self.year)

  def is_current_planner(self):
    year, sem = self.get_current_year_and_sem()
    if int(self.year) == year and self.semester.id == sem.id:
      return True
    return False

  def is_next_planner(self):
    year, sem = self.get_current_year_and_sem()
    try:
      ctp = TrainingPlanner.objects.get(year=year, semester=sem)
      year = int(ctp.year)
      even = True
      if ctp.semester.even:
        year = year + 1
        even = False
      if int(self.year) == year and bool(self.semester.even) == even:
        return True
    except:
      pass
    return False

  def get_current_year_and_sem(self):
    now = datetime.now()
    year = now.year
    month = now.month
    is_even = True
    # finding semester
    if month > 6 and month < 13:
      sem = Semester.objects.get(name='Odd')
      is_even = False
    else:
      sem = Semester.objects.get(name='Even')
    # finding year
    if is_even:
      year = year - 1
    return year, sem

  def completed_training(self):
    return self.training_requests().filter(status=1)

  def ongoing_training(self):
    return self.training_requests().filter(status=0)

  def is_full(self, department_id):
    if self.training_requests().filter(department_id=department_id).count() > 3:
      return True
    return False
  
  # todo with test without test
  def is_course_full(self, category, department_id):
    if self.training_requests().filter(department_id=department_id, course__category = category, course__test = True).count() > 1:
      return True
    elif self.training_requests().filter(department_id=department_id, course__category = category, course__test = False).count() > 2:
      return True
    return False

  def is_unmapped_course_full(self, department_id):
    if self.training_requests().filter(department_id=department_id, course__category = 2).count() > 4:
      return True
    return False

  def get_current_semester_date_duration(self):
    if self.semester.even:
      return datetime.strptime(str(int(self.year)+1)+'-01-01', '%Y-%m-%d').date(), datetime.strptime(str(int(self.year)+1)+'-06-30', '%Y-%m-%d').date()
    return datetime.strptime(str(self.year)+'-07-01', '%Y-%m-%d').date(), datetime.strptime(str(self.year)+'-12-31', '%Y-%m-%d').date()

  class Meta:
    unique_together = ("year", "academic", "organiser", "semester")

class TrainingRequest(models.Model):
  training_planner = models.ForeignKey(TrainingPlanner)
  department = models.ForeignKey(Department)
  sem_start_date = models.DateField()
  course = models.ForeignKey(CourseMap)
  batch = models.ForeignKey(StudentBatch, null = True)
  participants = models.PositiveIntegerField(default=0)
  status = models.BooleanField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  #created = models.DateTimeField()
  #updated = models.DateTimeField()
  
  # restrict the month to rise a training request
  def can_mark_attendance(self):
    sem_start, sem_end = self.training_planner.get_current_semester_date_duration()
    today = date.today()
    if self.status or today < self.sem_start_date or today > sem_end:
      return False
    elif self.course.category == 0 and date.today() > self.sem_start_date:
      return False
    return True

  def update_participants_count(self):
    self.participants = TrainingAttend.objects.filter(training_id = self.id).count()
    self.save()
    return self.participants

  def attendance_summery(self):
    if self.status == 1:
      return self.participants
    training_attend_count = TrainingAttend.objects.filter(training_id = self.id).count()
    student_master_count = StudentMaster.objects.filter(batch_id=self.batch_id).count()
    return '(%d / %d)' % (training_attend_count, student_master_count)

  def can_edit(self):
    if self.status or TrainingAttend.objects.filter(training_id=self.id).exists():
      return False
    return True

class TrainingAttend(models.Model):
  training = models.ForeignKey(TrainingRequest)
  student = models.ForeignKey(Student)
  language = models.ForeignKey(Language, default=None)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  #created = models.DateTimeField()
  #updated = models.DateTimeField()

  class Meta:
    unique_together = ("training", "student")

class TrainingCertificate(models.Model):
  student = models.ForeignKey(Student)
  training = models.ForeignKey(TrainingRequest)
  password = models.CharField(max_length = 255, null = True)
  count = models.PositiveSmallIntegerField(default=0)
  #updated = models.DateTimeField(auto_now = True)
  updated = models.DateTimeField()

  def __unicode__(self):
    return self.student

# School, Live Workshop, Pilot Workshop
class SingleTraining(models.Model):
  organiser = models.ForeignKey(Organiser)
  academic = models.ForeignKey(AcademicCenter)
  course = models.ForeignKey(CourseMap) # type 0
  # {0:School, 1:Live Workshop, 2:Pilot Workshop}
  training_type = models.PositiveIntegerField(default=0)
  language = models.ForeignKey(Language)
  tdate = models.DateField()
  ttime = models.TimeField()
  #{0:request done, 1: attendance submited, 2: completed}
  status = models.PositiveSmallIntegerField(default=0)
  participant_count = models.PositiveIntegerField(default=0)
  #created = models.DateTimeField(auto_now_add = True)
  #updated = models.DateTimeField(auto_now = True)
  created = models.DateTimeField()
  updated = models.DateTimeField()

  class Meta:
    unique_together = (("organiser", "academic", "course", "tdate", "ttime"),)

class SingleTrainingAttendance(models.Model):
  training = models.ForeignKey(SingleTraining)
  firstname = models.CharField(max_length = 100, null=True)
  lastname = models.CharField(max_length = 100, null=True)
  gender = models.CharField(max_length=10, null=True)
  email = models.EmailField(null=True)
  password = models.CharField(max_length = 100, null=True)
  count = models.PositiveSmallIntegerField(default=0)
  # {0:waiting for confirmation, 1:approved, 2:complete}
  status = models.PositiveSmallIntegerField(default=0)
  #created = models.DateTimeField(auto_now_add = True)
  #updated = models.DateTimeField(auto_now = True)
  created = models.DateTimeField()
  updated = models.DateTimeField()

  class Meta:
    unique_together = (("training", "firstname", "lastname", "email"),)

### Signals
def revoke_student_permission(sender, instance, *args, **kwargs):
  try:
    group = instance.user.groups.get(name='Student')
    group.user_set.remove(instance.user)
  except:
    pass

pre_delete.connect(revoke_student_permission, sender=Student)
