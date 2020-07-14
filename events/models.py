
from builtins import str
from builtins import object
from django.db import models
from datetime import datetime, date, timedelta
from django.db.models.signals import pre_delete, post_delete
from django.dispatch import receiver
from django.db.models import Q, Count, Sum, Min
from django.utils.encoding import python_2_unicode_compatible

#import auth user models
from django.contrib.auth.models import User

#validation
from django.core.exceptions import ValidationError

# importing models to access moodle DB
from mdldjango.models import *

# importing from events.signals
from events.signals import revoke_student_permission

#creation app models
from creation.models import FossCategory, Language, \
  FossAvailableForWorkshop, FossAvailableForTest


# Create your models here.
@python_2_unicode_compatible
class State(models.Model):
  users = models.ManyToManyField(
    User,
    related_name="resource_person",
    through='ResourcePerson'
  )
  code = models.CharField(max_length=3)
  name = models.CharField(max_length=50)
  slug = models.CharField(max_length = 100)
  latitude = models.DecimalField(
    null=True,
    max_digits=10,
    decimal_places=4,
    blank=True
  )
  longtitude = models.DecimalField(
    null=True,
    max_digits=10,
    decimal_places=4,
    blank=True
  )
  img_map_area = models.TextField()
  has_map = models.BooleanField(default=1)
  created = models.DateTimeField(auto_now_add = True, null=True)
  updated = models.DateTimeField(auto_now = True, null=True)

  def __str__(self):
    return self.name

  class Meta(object):
    unique_together = (("code","name"),)


@python_2_unicode_compatible
class District(models.Model):
  state = models.ForeignKey(State, on_delete=models.PROTECT )
  code = models.CharField(max_length=3)
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True, null=True)
  updated = models.DateTimeField(auto_now = True, null=True)

  def __str__(self):
    return self.name

  class Meta(object):
    unique_together = (("state", "code","name"),)
    #unique_together = (("state_id","name"),)


@python_2_unicode_compatible
class City(models.Model):
  state = models.ForeignKey(State, on_delete=models.PROTECT )
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True, null=True)
  updated = models.DateTimeField(auto_now = True, null=True)

  def __str__(self):
    return self.name

  class Meta(object):
    unique_together = (("name","state"),)


@python_2_unicode_compatible
class Location(models.Model):
  district = models.ForeignKey(District, on_delete=models.PROTECT )
  name = models.CharField(max_length=200)
  pincode = models.PositiveIntegerField()
  created = models.DateTimeField(auto_now_add = True, null=True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.name

  class Meta(object):
    unique_together = (("name","district","pincode"),)


class ResourcePerson(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT )
  state = models.ForeignKey(State, on_delete=models.PROTECT )
  assigned_by = models.PositiveIntegerField()
  status = models.BooleanField()
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  class Meta(object):
    verbose_name = "Resource Person"
    unique_together = (("user","state"),)


@python_2_unicode_compatible
class University(models.Model):
  name = models.CharField(max_length=200)
  state = models.ForeignKey(State, on_delete=models.PROTECT )
  user = models.ForeignKey(User, on_delete=models.PROTECT )
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.name

  class Meta(object):
    unique_together = (("name","state"),)


@python_2_unicode_compatible
class InstituteCategory(models.Model):
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.name

  class Meta(object):
    verbose_name = "Institute Categorie"


@python_2_unicode_compatible
class InstituteType(models.Model):
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.name

  class Meta(object):
    unique_together = (("name"),)


@python_2_unicode_compatible
class AcademicCenter(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT )
  state = models.ForeignKey(State, on_delete=models.PROTECT )
  institution_type = models.ForeignKey(InstituteType, on_delete=models.PROTECT )
  institute_category = models.ForeignKey(InstituteCategory, on_delete=models.PROTECT )
  university = models.ForeignKey(University, on_delete=models.PROTECT )
  academic_code = models.CharField(max_length=100, unique = True)
  institution_name = models.CharField(max_length=200)
  district = models.ForeignKey(District, on_delete=models.PROTECT )
  location = models.ForeignKey(Location, null=True, on_delete=models.PROTECT )
  city = models.ForeignKey(City, on_delete=models.PROTECT )
  address = models.TextField()
  pincode = models.PositiveIntegerField()
  resource_center = models.BooleanField()
  rating = models.PositiveSmallIntegerField()
  contact_person = models.TextField()
  remarks = models.TextField()
  status = models.PositiveSmallIntegerField()
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  class Meta(object):
    verbose_name = "Academic Center"
    #unique_together = (
    #  ("institution_name","district"),
    #  ("institution_name","university")
    #)

  def __str__(self):
    return self.institution_name

  def get_training_count(self):
    return TrainingRequest.objects.filter(
      training_planner__academic_id=self.id,
      participants__gt=0,
      sem_start_date__lte=datetime.now()
    ).count()

  def get_training_participant_count(self):
    training = TrainingRequest.objects.filter(
      training_planner__academic_id=self.id,
      participants__gt=0,
      sem_start_date__lte=datetime.now()
    ).aggregate(Sum('participants'))
    return training['participants__sum']

@python_2_unicode_compatible
class Accountexecutive(models.Model):
  user = models.OneToOneField(User, related_name = 'accountexecutive', on_delete=models.PROTECT )
  appoved_by = models.ForeignKey(
    User,
    related_name = 'accountexecutive_approved_by',
    blank=True,
    null=True, on_delete=models.PROTECT )
  academic = models.ForeignKey(AcademicCenter, blank=True, null=True, on_delete=models.PROTECT )
  status = models.PositiveSmallIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.user.username


@python_2_unicode_compatible
class Organiser(models.Model):
  user = models.OneToOneField(User, related_name = 'organiser', on_delete=models.PROTECT )
  appoved_by = models.ForeignKey(
    User,
    related_name = 'organiser_approved_by',
    blank=True,
    null=True, on_delete=models.PROTECT )
  academic = models.ForeignKey(AcademicCenter, blank=True, null=True, on_delete=models.PROTECT )
  status = models.PositiveSmallIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.user.username


@python_2_unicode_compatible
class Invigilator(models.Model):
  user = models.OneToOneField(User, on_delete=models.PROTECT )
  appoved_by = models.ForeignKey(
    User,
    related_name = 'invigilator_approved_by',
    blank=True,
    null=True,  on_delete=models.PROTECT )
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  status = models.PositiveSmallIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.user.username


@python_2_unicode_compatible
class Department(models.Model):
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.name

  class Meta(object):
    ordering = ['name']


@python_2_unicode_compatible
class Course(models.Model):
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.name

  class Meta(object):
    unique_together = (("name"),)


class TrainingExtraFields(models.Model):
  paper_name = models.CharField(max_length = 200)
  approximate_hour = models.PositiveIntegerField(default = 0)
  online_test = models.PositiveIntegerField(default = 0)
  is_tutorial_useful = models.BooleanField(default = 0)
  future_training = models.BooleanField(default = 0)
  recommend_to_others = models.BooleanField(default = 0)
  no_of_lab_session = models.CharField(max_length = 30, null=True)

class Training(models.Model):
  organiser = models.ForeignKey(Organiser, on_delete=models.PROTECT )
  appoved_by = models.ForeignKey(
    User,
    related_name = 'training_approved_by',
    null=True,  on_delete=models.PROTECT )
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  course = models.ForeignKey(Course, on_delete=models.PROTECT )
  training_type = models.PositiveIntegerField(default=0)
  training_code = models.CharField(max_length=100, null=True)
  department = models.ManyToManyField(Department)
  language = models.ForeignKey(Language, on_delete=models.PROTECT )
  foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
  tdate = models.DateField()
  ttime = models.TimeField()
  skype = models.PositiveSmallIntegerField(default=0)
  status = models.PositiveSmallIntegerField(default=0)
  # 0:request done, 1: attendance submit, 2: training manger approved,
  # 3: mark attenda done, 4: complete, 5: rejected
  extra_fields = models.OneToOneField(TrainingExtraFields, null = True, on_delete=models.PROTECT )
  participant_count = models.PositiveIntegerField(default=0)
  trusted = models.BooleanField(default=1)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  class Meta(object):
    unique_together = (("organiser", "academic", "foss", "tdate", "ttime"),)


class TrainingAttendance(models.Model):
  training = models.ForeignKey(Training, on_delete=models.PROTECT )
  mdluser_id = models.PositiveIntegerField(null=True, blank=True)
  firstname = models.CharField(max_length = 100, null=True)
  lastname = models.CharField(max_length = 100, null=True)
  gender = models.CharField(max_length=10, null=True)
  email = models.EmailField(null=True)
  password = models.CharField(max_length = 100, null=True)
  count = models.PositiveSmallIntegerField(default=0)
  status = models.PositiveSmallIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  class Meta(object):
    verbose_name = "Training Attendance"
    #unique_together = (("training", "mdluser_id"))


class TrainingLog(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT )
  training = models.ForeignKey(Training, on_delete=models.PROTECT )
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  role = models.PositiveSmallIntegerField()
  #{0:'organiser', 1:'ResourcePerson', 2: 'Event Manager'}
  status = models.PositiveSmallIntegerField()
  # {0:'new', 1:'approved', 2:'completed', 3: 'rejected', 4:'update',
  # 5:'Offline-Attendance submited', 6:'Marked Attendance'}
  created = models.DateTimeField(auto_now_add = True)


@python_2_unicode_compatible
class TestCategory(models.Model):
  name = models.CharField(max_length=200)
  status = models.BooleanField(default = 0)
  created = models.DateTimeField(auto_now_add = True, null=True)
  updated = models.DateTimeField(auto_now = True, null=True)

  def __str__(self):
    return self.name


class Test(models.Model):
  organiser = models.ForeignKey(Organiser, related_name = 'test_organiser', on_delete=models.PROTECT )
  test_category = models.ForeignKey(
    TestCategory,
    related_name = 'category_tests', on_delete=models.PROTECT )
  appoved_by = models.ForeignKey(
    User,
    related_name = 'test_approved_by',
    null=True,  on_delete=models.PROTECT )
  invigilator = models.ForeignKey(
    Invigilator,
    related_name = 'test_invigilator',
    null=True,  on_delete=models.PROTECT )
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  department = models.ManyToManyField(Department)
  training = models.ForeignKey('TrainingRequest', null=True, on_delete=models.PROTECT )
  foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
  test_code = models.CharField(max_length=100)
  tdate = models.DateField()
  ttime = models.TimeField()
  status = models.PositiveSmallIntegerField(default=0)
  participant_count = models.PositiveIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  class Meta(object):
    verbose_name = "Test Categorie"
    unique_together = (("organiser", "academic", "foss", "tdate", "ttime"),)

  def get_test_attendance_count(self):
    return TestAttendance.objects.filter(
      test_id=self.id,
      status__gte=2
    ).count()

  def update_test_participant_count(self):
    self.participant_count = self.get_test_attendance_count()
    self.save()
    return self


class TestAttendance(models.Model):
  test = models.ForeignKey(Test, on_delete=models.PROTECT )
  student = models.ForeignKey('Student', null=True, on_delete=models.PROTECT )
  mdluser_firstname = models.CharField(max_length = 100)
  mdluser_lastname = models.CharField(max_length = 100)
  mdluser_id = models.PositiveIntegerField()
  mdlcourse_id = models.PositiveIntegerField(default=0)
  mdlquiz_id = models.PositiveIntegerField(default=0)
  mdlattempt_id = models.PositiveIntegerField(default=0)
  password = models.CharField(max_length = 100, null=True)
  count = models.PositiveSmallIntegerField(default=0)
  status = models.PositiveSmallIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  class Meta(object):
    verbose_name = "Test Attendance"
    unique_together = (("test", "mdluser_id"))


class TestLog(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT )
  test = models.ForeignKey(Test, on_delete=models.PROTECT )
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  role = models.PositiveSmallIntegerField(default=0)
  # {0:'organiser', 1:'invigilator', 2:'ResourcePerson', 3: 'Event Manager'}
  status = models.PositiveSmallIntegerField(default=0)
  # {0:'new', 1:'RP-approved', 2:'Inv-approved', 3: 'ongoing', 4:'completed',
  # 5:'Rp-rejected', 6:'Inv-rejected', 7:'Update',
  # 8:'Attendance submited', 9:'Marked Attendance'}
  created = models.DateTimeField(auto_now_add = True)


@python_2_unicode_compatible
class PermissionType(models.Model):
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  def __str__(self):
    return self.name


class Permission(models.Model):
  permissiontype = models.ForeignKey(PermissionType, on_delete=models.PROTECT )
  user = models.ForeignKey(User, related_name = 'permission_user', on_delete=models.PROTECT )
  state = models.ForeignKey(State, related_name = 'permission_state', on_delete=models.PROTECT )
  district = models.ForeignKey(
    District,
    related_name = 'permission_district',
    null=True,  on_delete=models.PROTECT )
  university = models.ForeignKey(
    University,
    related_name = 'permission_iniversity',
    null=True,  on_delete=models.PROTECT )
  institute_type = models.ForeignKey(
    InstituteType,
    related_name = 'permission_institution_type',
    null=True,  on_delete=models.PROTECT )
  institute = models.ForeignKey(
    AcademicCenter,
    related_name = 'permission_district',
    null=True,  on_delete=models.PROTECT )
  assigned_by = models.ForeignKey(
    User,
    related_name = 'permission_assigned_by', on_delete=models.PROTECT )
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)


class FossMdlCourses(models.Model):
  foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
  mdlcourse_id = models.PositiveIntegerField()
  mdlquiz_id = models.PositiveIntegerField()


class EventsNotification(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT )
  role = models.PositiveSmallIntegerField(default=0)
  # {0:'organiser', 1:'invigilator', 2:'ResourcePerson', 3: 'Event Manager'}
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  category = models.PositiveSmallIntegerField(default=0)
  # {'workshop', 'training', 'test'}
  categoryid = models.PositiveIntegerField(default=0)
  status = models.PositiveSmallIntegerField(default=0)
  # {0:'new', 1:'update', 2:'approved', 3:'attendance',
  # 4: 'completed', 5:'rejected'}
  message = models.CharField(max_length = 255)
  created = models.DateTimeField(auto_now_add = True)


class Testimonials(models.Model):
  user = models.ForeignKey(User, related_name = 'testimonial_created_by', on_delete=models.PROTECT )
  approved_by = models.ForeignKey(User, related_name = 'testimonial_approved_by', null=True, on_delete=models.PROTECT )
  user_name = models.CharField(max_length=200)
  actual_content = models.TextField()
  minified_content = models.TextField()
  short_description = models.TextField()
  source_title = models.CharField(max_length=200, null=True)
  source_link = models.URLField(null = True)
  status = models.PositiveSmallIntegerField(default = 0)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now = True, null=True)

@python_2_unicode_compatible
class MediaTestimonials(models.Model):
    '''
    This model is required for storing audio / video testimonials
    * path contains the location of the file,
    * user is the person who has send the testimonial.
    '''
    foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
    path = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    workshop_details = models.CharField(max_length=255, default='Workshop')
    content = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)

    class Meta(object):
        verbose_name = 'Media Testimonials'
        verbose_name_plural = 'Media Testimonials'

    def __str__(self):
        return self.path

class OrganiserNotification(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT )


################ EVENTS VERSION II MODELS ###################


# Create your models here.
@python_2_unicode_compatible
class Student(models.Model):
  user = models.OneToOneField(User, on_delete=models.PROTECT )
  gender = models.CharField(max_length = 15)
  verified = models.PositiveSmallIntegerField(default = 0)
  error = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.user.first_name

  def student_fullname(self):
    if self.user.first_name:
      return '%s %s' % (self.user.first_name, self.user.last_name)
    return self.user.username

  def is_student_has_attendance(self):
    if TrainingAttend.objects.filter(student_id=self.id).exists():
      return True
    return False


@python_2_unicode_compatible
class StudentBatch(models.Model):
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  organiser = models.ForeignKey(Organiser, on_delete=models.PROTECT )
  department = models.ForeignKey(Department, on_delete=models.PROTECT )
  year = models.PositiveIntegerField() # 2010-2014
  stcount = models.PositiveIntegerField(default=0)
  batch_name = models.CharField(max_length=200, null=True)

  def __str__(self):
    return '%s, %s Batch' % (self.department.name, self.year)

  def get_batch_info(self):
    return '%s, %s, %s Batch' % (self.academic, self.department.name, self.year)

  def student_count(self):
    return StudentMaster.objects.filter(batch_id = self.id).count()

  def can_add_student(self, organiser_id):
    organiser = Organiser.objects.get(pk=organiser_id)
    if self.organiser.academic_id == organiser.academic_id:
      return True
    return False

  def update_student_count(self):
    self.stcount = StudentMaster.objects.filter(batch_id = self.id).count()
    self.save()
    return self.stcount

  def is_foss_batch_acceptable(self, course_id):
    sm = StudentMaster.objects.filter(batch_id=self.id)
    for s in sm:
      if not TrainingAttend.objects.filter(
        student_id=s.student_id,
        training__course_id=course_id
      ).exists():
        return True
    return False

  def has_training(self):
    if self.trainingrequest_set.exists():
       return False
    return True

  def create_batch_name(self):
    batch_query = StudentBatch.objects.filter(department_id=self.department_id, year=self.year, organiser=self.organiser)
    b_count = batch_query.count()
    name =  str(self.department)+"-"+str(self.year)+"-"+str(b_count)

    for a in range(b_count+1):
      name =  str(self.department)+"-"+str(self.year)+"-"+str(a+1)
    
      if not batch_query.filter(batch_name=name).exists():
        self.batch_name = name
        self.save()
        break
    return name


class StudentMaster(models.Model):
  batch = models.ForeignKey(StudentBatch, on_delete=models.PROTECT )
  student = models.ForeignKey(Student, on_delete=models.PROTECT )
  moved = models.BooleanField(default=False)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  class Meta(object):
    unique_together = ("batch", "student")
    ordering = ["student__user__first_name"]

  def is_student_has_attendance(self):
    tids = TrainingRequest.objects.filter(batch=self.batch_id).values('id')
    if TrainingAttend.objects.filter(training_id__in=tids, student_id=self.student_id).exists():
      return True
    return False

# Update student count in batch when delete student from batch
@receiver(post_delete, sender=StudentMaster, dispatch_uid='update_batch_count')
def update_batch_count(sender, instance, **kwargs):
  instance.batch.update_student_count()


@python_2_unicode_compatible
class Semester(models.Model):
  name = models.CharField(max_length = 50)
  even = models.BooleanField(default = True)

  def __str__(self):
    return self.name


@python_2_unicode_compatible
class LabCourse(models.Model):
  name = models.CharField(max_length=200)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.name


@python_2_unicode_compatible
class CourseMap(models.Model):
  #name = models.CharField(max_length=200, null=True, blank=True)
  course = models.ForeignKey(LabCourse, null=True, blank=True, on_delete=models.PROTECT )
  foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
  test = models.BooleanField(default=False)
  # {0 => one day workshop, 1 => mapped course, 2 => unmapped course}
  category = models.PositiveIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    if self.course_id:
      return '%s (%s)' % (self.foss.foss, self.course.name)
    return self.foss.foss
  def course_name(self):
    if self.course_id:
      return '%s - %s' % (self.course.name, self.foss.foss)
    return self.foss

  def category_name(self):
    courses = {
      0 : 'Software Course outside lab hours',
      1 : 'Software Course mapped in lab hours',
      2 : 'Software Course unmapped in lab hours',
      3 : 'EduEasy Software',
      4 : 'other'
    }
    return courses[self.category]

  class Meta(object):
    unique_together = ("course", "foss", "category")
    ordering = ('foss',)


@python_2_unicode_compatible
class TrainingPlanner(models.Model):
  year = models.CharField(max_length = 50)
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  organiser = models.ForeignKey(Organiser, on_delete=models.PROTECT )
  semester = models.ForeignKey(Semester, on_delete=models.PROTECT )
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)

  def __str__(self):
    return self.semester.name

  def training_requests(self):
    return TrainingRequest.objects.filter(
      training_planner_id = self.id
    ).exclude(Q(participants=0)&Q(status=1))

  # Select all training which has no attendance
  def training_with_no_attend(self):
    return TrainingRequest.objects.filter(
      (Q(participants=0, status=0) | Q(participants=0, status=1)),
      training_planner_id = self.id
    )

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
      ctp = TrainingPlanner.objects.get(
        year=year,
        semester=sem,
        organiser=self.organiser,
        academic=self.academic
      )
      year = int(ctp.year)
      even = True
      if ctp.semester.even:
        year = year + 1
        even = False
      if int(self.year) == year and bool(self.semester.even) == even:
        return True
    except Exception as e:
      print(e)
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

  def is_full(self, department_id, batch_id):
    if self.training_requests().filter(
      department_id=department_id,
      batch_id=batch_id,
      training_planner__semester=self.semester
    ).count() > 2:
      return True
    return False

  def is_school_full(self, department_id, batch_id):
    if self.training_requests().filter(
      department_id=department_id,
      batch_id=batch_id
    ).count() > 11:
      return True
    return False

  def get_current_semester_date_duration(self):
    if self.semester.even:
      return datetime.strptime(
          str(int(self.year)+1)+'-01-01', '%Y-%m-%d'
        ).date(), datetime.strptime(
          str(int(self.year)+1)+'-06-30', '%Y-%m-%d'
        ).date()
    return datetime.strptime(
      str(self.year)+'-07-01', '%Y-%m-%d'
    ).date(), datetime.strptime(
      str(self.year)+'-12-31', '%Y-%m-%d'
    ).date()

  def get_current_semester_date_duration_new(self):
    if self.semester.even:
      return datetime.strptime(
        str(int(self.year)+1)+'-01-01', '%Y-%m-%d'
      ).date(), datetime.strptime(
        str(int(self.year)+1)+'-03-31', '%Y-%m-%d'
      ).date()
    return datetime.strptime(
      str(self.year)+'-07-01', '%Y-%m-%d'
    ).date(), datetime.strptime(
      str(self.year)+'-9-30', '%Y-%m-%d'
    ).date()

  class Meta(object):
    unique_together = ("year", "academic", "organiser", "semester")


class TestTrainingManager(models.Manager):
  def get_queryset(self):
    return super(TestTrainingManager, self).get_queryset().filter(
      (
        Q(course__category=0) &
        #Q(status=1) &
        Q(sem_start_date__lte=datetime.now()-timedelta(days=15))
      ) |
      (
        Q(course__category__gt=0) &
        Q(sem_start_date__lte=datetime.now()-timedelta(days=15))
      ),
      participants__gt=0
    ).order_by('-training_planner__year', '-training_planner__semester_id')


class TrainingRequest(models.Model):
  training_planner = models.ForeignKey(TrainingPlanner, on_delete=models.PROTECT )
  department = models.ForeignKey(Department, on_delete=models.PROTECT )
  sem_start_date = models.DateField()
  training_start_date = models.DateField(default=datetime.now)
  training_end_date = models.DateField(default=datetime.now)
  course = models.ForeignKey(CourseMap, on_delete=models.PROTECT )
  batch = models.ForeignKey(StudentBatch, null = True, on_delete=models.PROTECT )
  participants = models.PositiveIntegerField(default=0)
  course_type = models.PositiveIntegerField(default=None)
  #status = models.BooleanField(default=False)
  status = models.PositiveSmallIntegerField(default=0)
  cert_status = models.PositiveSmallIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  #created = models.DateTimeField()
  #updated = models.DateTimeField()

  # managers
  objects = models.Manager() # The default manager.
  test_training = TestTrainingManager()

  # return course type
  def get_course_type(self):
    if self.course_type == 0:
      return 'Outside Lab Hours'
    elif self.course_type == 1:
      return 'Mapped Course'
    elif self.course_type == 2:
      return 'Unmapped Course'
    return ''

  def is_training_certificate_allowed(self):
    if not FossAvailableForTest.objects.filter(
      foss=self.course.foss,
      foss__status=True
    ).count():
      return True
    return False

  def is_learners_allowed(self):
    if FossCategory.objects.filter(
    id = self.course.foss.id, 
    is_learners_allowed=True,).count():
      return True
    return False

  def have_test(self):
    if FossAvailableForTest.objects.filter(foss=self.course.foss, foss__status=True).count():
      return True
    return False

  def is_training_before_july2017(self):
    d = date(2017,6,30)
    if self.sem_start_date < d:
      return True
    return False

  def is_certificate_not_allowed(self):
    if self.course.foss.id in [4,12,34,35,76]:
      return True
    return False

  # restrict the month to rise a training request
  def can_mark_attendance(self):
    sem_start, sem_end = self.training_planner.get_current_semester_date_duration()
    today = date.today()
    if self.status == 1 or today < self.sem_start_date or today > sem_end:
      return False
    #elif self.course.category == 0 and date.today() > self.sem_start_date:
      #return False
    return True

  def update_participants_count(self):
    self.participants = TrainingAttend.objects.filter(
      training_id = self.id
    ).count()
    self.save()
    return self.participants

  def get_partipants_from_attendance(self):
    return TrainingAttend.objects.filter(training_id = self.id).count()

  def get_partipants_from_batch(self):
    if self.batch:
      return self.batch.stcount
    return 0

  def attendance_summery(self):
    if self.status == 1:
      return self.participants
    training_attend_count = TrainingAttend.objects.filter(
      training_id = self.id
    ).count()
    student_master_count = StudentMaster.objects.filter(
      batch_id=self.batch_id
    ).count()
    return '(%d / %d)' % (training_attend_count, student_master_count)

  def can_edit(self):
    if self.status == 1 or TrainingAttend.objects.filter(training_id=self.id).exclude(training__department_id=169).exists():
      return False
    return True

  def training_name(self):
    if self.batch:
      return 'WC-{0}, {1}, {2} - {3} - {4}'.format(self.id, self.course, self.batch, \
        self.training_planner.year, int(self.training_planner.year)+1)
    return 'WC-{0}, {1}, {2} - {3}'.format(self.id, self.course, \
      self.training_planner.year, int(self.training_planner.year)+1)


class TrainingAttend(models.Model):
  training = models.ForeignKey(TrainingRequest, on_delete=models.PROTECT )
  student = models.ForeignKey(Student, on_delete=models.PROTECT )
  language = models.ForeignKey(Language, default=None, on_delete=models.PROTECT )
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  #created = models.DateTimeField()
  #updated = models.DateTimeField()

  class Meta(object):
    unique_together = ("training", "student")


@python_2_unicode_compatible
class TrainingCertificate(models.Model):
  student = models.ForeignKey(Student, on_delete=models.PROTECT )
  training = models.ForeignKey(TrainingRequest, on_delete=models.PROTECT )
  password = models.CharField(max_length = 255, null = True)
  count = models.PositiveSmallIntegerField(default=0)
  #updated = models.DateTimeField(auto_now = True)
  updated = models.DateTimeField()

  def __str__(self):
    return self.student


class TrainingFeedback(models.Model):
  training = models.ForeignKey(TrainingRequest, on_delete=models.PROTECT )
  mdluser_id = models.PositiveIntegerField()
  rate_workshop = models.PositiveSmallIntegerField()

  content = models.PositiveSmallIntegerField()
  sequence = models.PositiveSmallIntegerField()
  clarity = models.PositiveSmallIntegerField()
  interesting = models.PositiveSmallIntegerField()
  appropriate_example = models.PositiveSmallIntegerField()
  instruction_sheet = models.PositiveSmallIntegerField()
  assignment = models.PositiveSmallIntegerField()

  pace_of_tutorial = models.PositiveSmallIntegerField()
  workshop_learnt = models.TextField()
  weakness_workshop = models.BooleanField()
  weakness_narration = models.BooleanField()
  weakness_understand = models.BooleanField()
  other_weakness = models.TextField()
  tutorial_language = models.PositiveSmallIntegerField()
  apply_information = models.PositiveSmallIntegerField()
  if_apply_information_yes = models.TextField()

  setup_learning = models.PositiveSmallIntegerField()
  computers_lab = models.PositiveSmallIntegerField()
  audio_quality = models.PositiveSmallIntegerField()
  video_quality = models.PositiveSmallIntegerField()

  workshop_orgainsation = models.PositiveSmallIntegerField()
  faciliate_learning = models.PositiveSmallIntegerField()
  motivate_learners = models.PositiveSmallIntegerField()
  time_management = models.PositiveSmallIntegerField()

  knowledge_about_software = models.PositiveSmallIntegerField()
  provide_clear_explanation = models.PositiveSmallIntegerField()
  answered_questions = models.PositiveSmallIntegerField()
  interested_helping = models.PositiveSmallIntegerField()
  executed_workshop = models.PositiveSmallIntegerField()
  workshop_improved = models.TextField()

  recommend_workshop = models.PositiveSmallIntegerField()
  reason_why = models.TextField()
  other_comments = models.TextField()
  created = models.DateTimeField(auto_now_add = True)
  class Meta(object):
    unique_together = (("training", "mdluser_id"))


class TrainingLanguageFeedback(models.Model):
  training = models.ForeignKey(TrainingRequest, on_delete=models.PROTECT )
  mdluser_id = models.PositiveIntegerField()
  name = models.CharField(max_length=100, null=True, default=None)
  age = models.PositiveIntegerField()
  medium_of_instruction = models.PositiveIntegerField()
  gender = models.BooleanField()
  language_prefered = models.ForeignKey(Language, null=True, on_delete=models.PROTECT )
  tutorial_was_useful = models.PositiveIntegerField()
  learning_experience = models.PositiveIntegerField()
  satisfied_with_learning_experience = models.PositiveIntegerField()
  concept_explain_clearity = models.PositiveIntegerField()
  overall_learning_experience = models.PositiveIntegerField()
  user_interface = models.PositiveIntegerField()
  understanding_difficult_concept = models.PositiveIntegerField()
  curious_and_motivated = models.PositiveIntegerField()
  similar_tutorial_with_other_content = models.PositiveIntegerField()
  foss_tutorial_was_mentally_demanding = models.PositiveIntegerField()
  side_by_side_method_is_understood = models.PositiveIntegerField(default=0)

  compfortable_learning_in_language = models.PositiveIntegerField()
  confidence_level_in_language = models.PositiveIntegerField()
  preferred_language = models.PositiveIntegerField()
  preferred_language_reason = models.TextField()
  prefer_translation_in_mother_tongue = models.PositiveIntegerField()
  prefer_translation_in_mother_tongue_reason = models.TextField()
  side_by_side_method_meant = models.PositiveIntegerField()
  side_by_side_method_is_beneficial = models.PositiveIntegerField()
  side_by_side_method_is_beneficial_reason = models.TextField()
  limitations_of_side_by_side_method = models.TextField()

  content_information_flow = models.PositiveIntegerField()
  content_appropriate_examples = models.PositiveIntegerField()
  content_ease_of_understanding = models.PositiveIntegerField()
  content_clarity_of_instruction_sheet = models.PositiveIntegerField()
  content_ease_of_performing_assignment = models.PositiveIntegerField()
  content_best_features = models.TextField()
  content_areas_of_improvement = models.TextField()

  video_audio_video_synchronization = models.PositiveIntegerField()
  video_attractive_color_features = models.PositiveIntegerField()
  video_text_readable = models.PositiveIntegerField()
  video_best_features = models.TextField()
  video_areas_of_improvement = models.TextField()

  audio_pleasant_speech_and_accent = models.PositiveIntegerField()
  audio_soothing_and_friendly_tone = models.PositiveIntegerField()
  audio_understandable_and_clear_speech = models.PositiveIntegerField()
  audio_best_features = models.TextField()
  audio_areas_of_improvement = models.TextField()

  side_by_side_method_is_effective = models.PositiveIntegerField(default=0)
  side_by_side_method_is = models.PositiveIntegerField(default=0)

  created = models.DateTimeField(auto_now_add = True)
  class Meta(object):
    unique_together = (("training", "mdluser_id"))


# School, Live Workshop, Pilot Workshop
class SingleTraining(models.Model):
  organiser = models.ForeignKey(Organiser, on_delete=models.PROTECT )
  state = models.ForeignKey(State, null=True, on_delete=models.PROTECT )
  institution_type = models.ForeignKey(InstituteType, null=True, on_delete=models.PROTECT )
  academic = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  course = models.ForeignKey(CourseMap, on_delete=models.PROTECT ) # type 0
  # {0:School, 3:Vocational, 1:Live Workshop, 2:Pilot Workshop}
  training_type = models.PositiveIntegerField(default=0)
  language = models.ForeignKey(Language, on_delete=models.PROTECT )
  tdate = models.DateField()
  ttime = models.TimeField(null=True, blank=True)
  #{0:request done, 1: attendance submited, 2: completed}
  status = models.PositiveSmallIntegerField(default=0)
  participant_count = models.PositiveIntegerField(default=0)
  total_participant_count = models.PositiveIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  #created = models.DateTimeField()
  #updated = models.DateTimeField()

  def is_singletraining_certificate_allowed(self):
    if not FossAvailableForTest.objects.filter(
      foss=self.course.foss,
      foss__status=True
    ).count():
      return True
    return False

  class Meta(object):
    unique_together = (("organiser", "academic", "course", "tdate", "ttime"),)


class SingleTrainingAttendance(models.Model):
  training = models.ForeignKey(SingleTraining, on_delete=models.PROTECT )
  foss = models.PositiveIntegerField(default=0)
  firstname = models.CharField(max_length = 100, null=True)
  lastname = models.CharField(max_length = 100, null=True)
  gender = models.CharField(max_length=10, null=True)
  email = models.EmailField(null=True)
  password = models.CharField(max_length = 100, null=True)
  count = models.PositiveSmallIntegerField(default=0)
  # {0:waiting for confirmation, 1:approved, 2:complete}
  status = models.PositiveSmallIntegerField(default=0)
  created = models.DateTimeField(auto_now_add = True)
  updated = models.DateTimeField(auto_now = True)
  #created = models.DateTimeField()
  #updated = models.DateTimeField()

  class Meta(object):
    unique_together = (("training", "firstname", "lastname", "email"),)


class TrainingLiveFeedback(models.Model):
  training = models.ForeignKey(SingleTraining, on_delete=models.PROTECT )

  rate_workshop = models.PositiveSmallIntegerField()

  name = models.CharField(max_length=100)
  email = models.EmailField()
  branch = models.CharField(max_length=100)
  institution = models.CharField(max_length=100)

  content = models.PositiveSmallIntegerField()
  sequence = models.PositiveSmallIntegerField()
  clarity = models.PositiveSmallIntegerField()
  interesting = models.PositiveSmallIntegerField()
  appropriate_example = models.PositiveSmallIntegerField()
  instruction_sheet = models.PositiveSmallIntegerField()
  assignment = models.PositiveSmallIntegerField()

  pace_of_tutorial = models.PositiveSmallIntegerField()
  workshop_learnt = models.TextField()
  weakness_workshop = models.BooleanField()
  weakness_narration = models.BooleanField()
  weakness_understand = models.BooleanField()
  other_weakness = models.TextField()
  tutorial_language = models.PositiveSmallIntegerField()
  apply_information = models.PositiveSmallIntegerField()
  if_apply_information_yes = models.TextField()

  setup_learning = models.PositiveSmallIntegerField()
  computers_lab = models.PositiveSmallIntegerField()
  audio_quality = models.PositiveSmallIntegerField()
  video_quality = models.PositiveSmallIntegerField()

  workshop_orgainsation = models.PositiveSmallIntegerField()
  faciliate_learning = models.PositiveSmallIntegerField()
  motivate_learners = models.PositiveSmallIntegerField()
  time_management = models.PositiveSmallIntegerField()

  knowledge_about_software = models.PositiveSmallIntegerField()
  provide_clear_explanation = models.PositiveSmallIntegerField()
  answered_questions = models.PositiveSmallIntegerField()
  interested_helping = models.PositiveSmallIntegerField()
  executed_workshop = models.PositiveSmallIntegerField()
  workshop_improved = models.TextField()

  recommend_workshop = models.PositiveSmallIntegerField()
  reason_why = models.TextField()
  other_comments = models.TextField()
  created = models.DateTimeField(auto_now_add = True)

  class Meta(object):
    unique_together = (("training", "email"))


### Signals
pre_delete.connect(revoke_student_permission, sender=Student)

@python_2_unicode_compatible
class StudentStream(models.Model):
  STUDENT_STREAM_CHOICES = (
  ('0', 'Engineering'), ('1', 'Science'), ('2', 'Arts and Humanities'),('3', 'Polytechnic/ Diploma programs'),
  ('4', 'Commerce and Business Studies'),('5', 'ITI'),('6', 'Other')
  )
  student_stream = models.CharField(max_length =50, choices = STUDENT_STREAM_CHOICES)

  def __str__(self):
        return self.student_stream

@python_2_unicode_compatible
class HelpfulFor(models.Model):
  HELPFUL_FOR_CHOICES = (
  ('0', 'Academic Performance'), ('1', 'Project Assignments'), ('2', 'To get job interviews'),('3', 'To get jobs'),
  ('4', 'All of the above')
  )
  helpful_for = models.CharField(max_length = 50, choices = HELPFUL_FOR_CHOICES)

  def __str__(self):
        return self.helpful_for

class OrganiserFeedback(models.Model):
  IS_SPOKEN_HELPFUL_CHOICES = (
    ('','-----'), ('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'),
    ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea'))
  RATE_SPOKEN_CHOICES = (
    ('','-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Verybad', 'Very bad'))
  YES_NO_CHOICES =(
    ('','-----'), ('Yes', 'Yes'), ('No', 'No'),
  )
  AGE_CHOICES = (
    ('', '-----'), ('<25', '<25 years'), ('25-35', '25-35 years'), ('35+', '35 years and above'),
  )
  GENDER_CHOICES =(
    ('', '-----'), ('Male', 'Male'), ('Female', 'Female'),
  )
  DESIGNATION_CHOICES = (
    ('', '-----'), ('Student', 'Student'), ('Faculty', 'Faculty'), ('Staff', 'Staff'), ('Admin', 'Admin'),
  )
  MEDIUM_OF_INSTRUCTION_CHOICES = (
    ('', '-----'), ('English', 'English'), ('Vernacular', 'Vernacular'), ('Mixed', 'Mixed'),
  )
  STUDENT_EDUCATION_LANGUAGE_CHOICES = (
    ('', '-----'), ('English', 'Mostly English'), ('Vernacular', 'Mostly Vernacular'), ('Mixed', 'Mostly Mixed')
  )
  STUDENT_GENDER_CHOICES = (
    ('', '-----'), ('Male', 'Mostly Male'), ('Female', 'Mostly Female'), ('Mixed', 'Mixed')
  )
  STUDENT_LOCATION_CHOICES = (
    ('', '-----'), ('Urban', 'Mainly Urban'), ('Rural', 'Mainly Rural'), ('Mixed', 'Mixed'), ('Notsure', 'Not sure')
  )
  DURATION_OF_TUTORIAL_CHOICES = (
    ('', '-----'), ('<0.5', 'Less than 0.5 hour'), ('0.5-2', '0.5 - 2 hour'), ('2-10', '2-10 hours'),('10+', 'Above 10 hours'),('NA', 'Not applicable')
  )
  SIDE_BY_SIDE_METHOD_IS_CHOICES = (
    ('', '-----'), ('0', 'Explaining the video to a neighbor'), ('1', 'Waiting for mentors explanation'), ('2', 'Watching and practicing simultaneously'), ('3', 'Dont know what this method is')
  )
  IN_SIDE_BY_SIDE_METHOD_CHOICES = (
    ('', '-----'), ('0', 'The video has to be maximized'), ('1', 'The software has to be maximized'), ('2', 'Both software and video are maximized'), ('3', 'None of the above are maximized')
  )
  GOOD_INVESTMENT_CHOICES = (
    ('', '-----'), ('Yes', 'Yes'), ('No', 'No'), ('Notsure', 'Not sure')
  )

  name = models.CharField(max_length = 100)
  email = models.EmailField(max_length = 100)
  gender = models.CharField(max_length = 10, choices = GENDER_CHOICES)
  age = models.CharField(max_length = 20, choices = AGE_CHOICES)
  state = models.ForeignKey(State, on_delete=models.PROTECT )
  district =  models.ForeignKey(District, on_delete=models.PROTECT )
  city = models.ForeignKey(City, on_delete=models.PROTECT )
  university = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
  designation = models.CharField(max_length = 20, choices = DESIGNATION_CHOICES)
  medium_of_instruction = models.CharField(max_length =50, choices = MEDIUM_OF_INSTRUCTION_CHOICES)
  student_stream = models.ManyToManyField(StudentStream , related_name = 'events_StudentStream_related')
  student_education_language = models.CharField(max_length =50, choices = STUDENT_EDUCATION_LANGUAGE_CHOICES)
  student_gender =  models.CharField(max_length =50 ,choices = STUDENT_GENDER_CHOICES)
  student_location =  models.CharField(max_length =50,  choices = STUDENT_LOCATION_CHOICES)
  offered_training_foss = models.ManyToManyField(FossCategory , related_name = 'events_FossCategory_related')
  duration_of_tutorial =  models.CharField(max_length =50 ,choices = DURATION_OF_TUTORIAL_CHOICES)
  language = models.ManyToManyField(Language , related_name = 'events_Language_related')
  side_by_side_yes_no = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  side_by_side_method_is = models.CharField(max_length = 50, choices = SIDE_BY_SIDE_METHOD_IS_CHOICES)
  in_side_by_side_method = models.CharField(max_length = 50, choices = IN_SIDE_BY_SIDE_METHOD_CHOICES)
  good_investment = models.CharField(max_length = 50, choices = GOOD_INVESTMENT_CHOICES)
  helpful_for = models.ManyToManyField(HelpfulFor , related_name = 'events_HelpfulFor_related')
  is_comfortable_self_learning = models.CharField(max_length = 50, choices = IS_SPOKEN_HELPFUL_CHOICES)
  is_classroom_better = models.CharField(max_length = 50, choices = IS_SPOKEN_HELPFUL_CHOICES)
  is_student_expectations = models.CharField(max_length = 50, choices = IS_SPOKEN_HELPFUL_CHOICES)
  is_help_get_interview = models.CharField(max_length = 50, choices = IS_SPOKEN_HELPFUL_CHOICES)
  is_help_get_job = models.CharField(max_length = 50, choices = IS_SPOKEN_HELPFUL_CHOICES)
  is_got_job = models.CharField(max_length = 50, choices = IS_SPOKEN_HELPFUL_CHOICES)
  relevance = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  information_content = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  audio_video_quality = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  presentation_quality = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  overall_rating = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  trained_foss =  models.ManyToManyField(FossCategory)
  is_training_benefited = models.CharField(max_length = 50, choices = GOOD_INVESTMENT_CHOICES)
  testimonial = models.CharField(max_length = 500)
  any_other_suggestions = models.CharField(max_length = 500)
  can_contact = models.CharField(max_length = 50, choices = YES_NO_CHOICES)

def get_email_dir(instance, filename):
  email_dir = instance.email.replace('.','_')
  email_dir = email_dir.replace('@','on')
  return "latex/%s/%s" %(email_dir, filename)

class LatexWorkshopFileUpload(models.Model):
  email = models.EmailField()
  file_upload = models.FileField(upload_to=get_email_dir)

class STWorkshopFeedback(models.Model):
  YES_NO_CHOICES =(
    ('','-----'), ('Yes', 'Yes'), ('No', 'No'),
  )
  OPINION =(
    ('','-----'),('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'),
    ('StronglyDisagree', 'Strongly Disagree')
  )
  RATE_SPOKEN_CHOICES = (
    ('','-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')
  )
  GENDER_CHOICES =(
    ('', '-----'), ('Male', 'Male'), ('Female', 'Female'),
  )

  name = models.CharField(max_length = 100)
  email = models.EmailField(max_length = 100)
  gender = models.CharField(max_length = 10)
  age = models.CharField(max_length = 20)
  affiliation = models.CharField(max_length = 100)
  designation = models.CharField(max_length = 100, default=None)
  educational_back = models.CharField(max_length = 100, default=None)
  foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
  venue = models.CharField(max_length = 100)
  workshop_date = models.DateField()
  total_tutorials1 = models.CharField(max_length = 20)
  language_of_tutorial = models.CharField(max_length = 20, default=None)
  
  acquired_knowledge =  models.CharField(max_length = 50, choices = OPINION)
  suff_instruction = models.CharField(max_length = 50, choices = OPINION)
  diff_instruction = models.CharField(max_length = 50, choices = OPINION)
  method_easy = models.CharField(max_length = 50, choices = OPINION)
  time_sufficient =models.CharField(max_length = 50, choices = OPINION)
  desired_objective = models.CharField(max_length = 50, choices = OPINION)
  recommend = models.CharField(max_length = 50, choices = OPINION)
  like_to_part = models.CharField(max_length = 50, choices = OPINION)
  side_by_side_effective = models.CharField(max_length = 50, choices = OPINION)
  dont_like_self_learning_method = models.CharField(max_length = 50, choices = OPINION, default=None)
  training_any_comment = models.CharField(max_length = 100)
  
  not_self_explanatory = models.CharField(max_length = 50, choices = OPINION)
  logical_sequence = models.CharField(max_length = 50, choices = OPINION)
  examples_help = models.CharField(max_length = 50, choices = OPINION)
  instructions_easy_to_follow = models.CharField(max_length = 50, choices = OPINION)
  difficult_instructions_in_tutorial = models.CharField(max_length = 50, choices = OPINION, default=None)
  translate = models.CharField(max_length = 50, choices = OPINION, default=None)
  content_any_comment = models.CharField(max_length = 100)
  
  useful_learning = models.CharField(max_length = 50, choices = OPINION)
  help_improve_performance = models.CharField(max_length = 50, choices = OPINION)
  plan_to_use_future = models.CharField(max_length = 50, choices = OPINION)
  confident_to_apply_knowledge = models.CharField(max_length = 50, choices = OPINION, default=None)
  difficult_simultaneously = models.CharField(max_length = 50, choices = OPINION)
  too_fast = models.CharField(max_length = 50, choices = OPINION, default=None)
  too_slow = models.CharField(max_length = 50, choices = OPINION, default=None)
  interface_comfortable = models.CharField(max_length = 50, choices = OPINION)
  satisfied = models.CharField(max_length = 50, choices = OPINION)
  self_learning_intrest = models.CharField(max_length = 50, choices = OPINION)
  language_diff_to_understand = models.CharField(max_length = 50, choices = OPINION, default=None)
  not_like_method_forums = models.CharField(max_length = 50, choices = OPINION)
  forum_helpful = models.CharField(max_length = 50, choices = OPINION)
  owing_to_forums = models.CharField(max_length = 50, choices = OPINION)
  learning_any_comment = models.CharField(max_length = 100)
  
  ws_quality = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  overall_content_quality = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  clarity_of_explanation = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  flow = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  relevance = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  guidelines = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  overall_video_quality = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  text_readability = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  clarity_of_speech = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  visual_presentation = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  pace_of_tutorial = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  time_management = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  experience_of_learning = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  overall_arrangement = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  like_abt_ws = models.CharField(max_length = 500)
  how_make_better = models.CharField(max_length = 500)
  experience = models.CharField(max_length = 500)
  suggestions = models.CharField(max_length = 500)
  created = models.DateTimeField(auto_now_add = True)

class STWorkshopFeedbackPre(models.Model):
  FEELINGS =(
    ('','-----'),('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'),
    ('Absolutelyconfident', 'Absolutely confident'),('NotApplicable', 'Not Applicable'))
  GENDER_CHOICES =(
    ('', '-----'), ('Male', 'Male'), ('Female', 'Female'),
  )
  user = models.ForeignKey(User, on_delete=models.PROTECT )
  email = models.EmailField(max_length = 100)
  gender = models.CharField(max_length = 10, choices = GENDER_CHOICES)
  age = models.CharField(max_length = 20)
  content_management = models.CharField(max_length = 50, choices = FEELINGS)
  configuration_management = models.CharField(max_length = 50, choices = FEELINGS)
  creating_basic_content = models.CharField(max_length = 50, choices = FEELINGS)
  edit_existing_content = models.CharField(max_length = 50, choices = FEELINGS)
  create_new_content = models.CharField(max_length = 50, choices = FEELINGS)
  grp_entity_ref = models.CharField(max_length = 50, choices = FEELINGS)
  taxonomy = models.CharField(max_length = 50, choices = FEELINGS)
  managing_content = models.CharField(max_length = 50, choices = FEELINGS)
  creating_dummy_content = models.CharField(max_length = 50, choices = FEELINGS)
  modify_display_content = models.CharField(max_length = 50, choices = FEELINGS)
  contents_using_view = models.CharField(max_length = 50, choices = FEELINGS)
  table_of_fields_with_views = models.CharField(max_length = 50, choices = FEELINGS)
  control_display_images = models.CharField(max_length = 50, choices = FEELINGS)
  adding_func = models.CharField(max_length = 50, choices = FEELINGS)
  finding_modules = models.CharField(max_length = 50, choices = FEELINGS)
  modifying_page_layout = models.CharField(max_length = 50, choices = FEELINGS)
  menu_endpoints = models.CharField(max_length = 50, choices = FEELINGS)
  styling_using_themes = models.CharField(max_length = 50, choices = FEELINGS)
  installig_ad_themes = models.CharField(max_length = 50, choices = FEELINGS)
  people_management = models.CharField(max_length = 50, choices = FEELINGS)
  site_management = models.CharField(max_length = 50, choices = FEELINGS)


class STWorkshopFeedbackPost(models.Model):
  YES_NO_CHOICES =(
    ('','-----'), ('Yes', 'Yes'), ('No', 'No'),
  )
  OPINION =(
    ('','-----'),('StronglyAgree', 'Strongly Agree'), ('Agree', 'Agree'), ('Neutral', 'Neutral'), ('Disagree', 'Disagree'),
    ('StronglyDisagree', 'Strongly Disagree'), ('Noidea', 'No idea')
  )
  RATE_SPOKEN_CHOICES = (
    ('','-----'), ('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair'), ('Bad', 'Bad'), ('Extremelybad', 'Extremely bad')
  )
  GENDER_CHOICES =(
    ('', '-----'), ('Male', 'Male'), ('Female', 'Female'),
  )
  FEELINGS =(
    ('','-----'),('Notconfidentatall', 'Not confident at all'), ('Unconfident', 'Unconfident'), ('Neitherconfidentnorunconfident', 'Neither confident nor unconfident'), ('Confident', 'Confident'),
    ('Absolutelyconfident', 'Absolutely confident'),('NotApplicable', 'Not Applicable'))

  FEES =(
    ('', '-----'), ('below250', 'Below Rs.250/-'),
    ('between251to500', 'Between Rs.251 to Rs.500/-'),
    ('between501to1000', 'Between Rs.501 to Rs.1000/-'),
    ('between1001to2000', 'Between Rs.1001 to Rs.2000/-'),
    ('above2000', 'Above Rs. 2000/-'),
  )

  NUM_OF_EXPERTS =(
    ('','-----'), ('1to10', '1 to 10'), ('11to20', '11 to 20'),('21to30', '21 to 30'),('31to40', '31 to 40'),('above40', 'Above 40'),
  )
  user = models.ForeignKey(User, on_delete=models.PROTECT )
  email = models.EmailField(max_length = 100)
  gender = models.CharField(max_length = 10, choices = GENDER_CHOICES)
  age = models.CharField(max_length = 20)
  participated_before = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  foss_where = models.CharField(max_length = 200)
  install_own = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  explain = models.CharField(max_length = 300)
  used_sw_before = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  sim_framework_before = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  total_tutorials1 = models.CharField(max_length = 20)
  purpose_of_attending = models.CharField(max_length = 300)


  spfriendly = models.CharField(max_length = 50, choices = OPINION)
  diff_watch_practice = models.CharField(max_length = 50, choices = OPINION)
  satisfied_with_learning_experience = models.CharField(max_length = 50, choices = OPINION)
  confident = models.CharField(max_length = 50, choices = OPINION)
  side_by_side_hold_intrest = models.CharField(max_length = 50, choices = OPINION)
  ws_not_useful = models.CharField(max_length = 50, choices = OPINION)
  can_learn_other = models.CharField(max_length = 50, choices = OPINION)
  wantto_conduct_incollege = models.CharField(max_length = 50, choices = OPINION)
  esy_to_conduct_own = models.CharField(max_length = 50, choices = OPINION)
  ask_student_to_use =  models.CharField(max_length = 50, choices = OPINION)
  possible_to_use_therotical = models.CharField(max_length = 50, choices = OPINION)


  not_self_explanatory = models.CharField(max_length = 50, choices = OPINION)
  logical_sequence = models.CharField(max_length = 50, choices = OPINION)
  examples_help = models.CharField(max_length = 50, choices = OPINION)
  other_language = models.CharField(max_length = 50, choices = OPINION)
  instructions_easy_to_follow = models.CharField(max_length = 50, choices = OPINION)
  language_complicated = models.CharField(max_length = 50, choices = OPINION)


  acquired_knowledge =  models.CharField(max_length = 50, choices = OPINION)
  suff_instruction_by_prof = models.CharField(max_length = 50, choices = OPINION)
  suff_instruction_by_staff = models.CharField(max_length = 50, choices = OPINION)
  method_easy = models.CharField(max_length = 50, choices = OPINION)
  desired_objective = models.CharField(max_length = 50, choices = OPINION)
  recommend = models.CharField(max_length = 50, choices = OPINION)
  like_to_part = models.CharField(max_length = 50, choices = OPINION)
  learn_other_side_by_side = models.CharField(max_length = 50, choices = OPINION)


  referred_forums = models.CharField(max_length = 50, choices = OPINION)
  referred_forums_after = models.CharField(max_length = 50, choices = OPINION)
  asked_ques_forums = models.CharField(max_length = 50, choices = OPINION)
  not_answer_doubts = models.CharField(max_length = 50, choices = OPINION)
  forum_helpful = models.CharField(max_length = 50, choices = OPINION)
  doubts_solved_fast = models.CharField(max_length = 50, choices = OPINION)
  need_not_post = models.CharField(max_length = 50, choices = OPINION)
  faster_on_forums = models.CharField(max_length = 50, choices = OPINION)
  not_have_to_wait = models.CharField(max_length = 50, choices = OPINION)
  not_like_method_forums = models.CharField(max_length = 50, choices = OPINION)
  helpful_pre_ans_ques = models.CharField(max_length = 50, choices = OPINION)
  not_like_reveal_identity = models.CharField(max_length = 50, choices = OPINION)
  forum_motivated = models.CharField(max_length = 50, choices = OPINION)
  per_asked_ques_before_tuts = models.CharField(max_length = 50, choices = OPINION)


  content_management = models.CharField(max_length = 50, choices = FEELINGS)
  configuration_management = models.CharField(max_length = 50, choices = FEELINGS)
  creating_basic_content = models.CharField(max_length = 50, choices = FEELINGS)
  edit_existing_content = models.CharField(max_length = 50, choices = FEELINGS)
  create_new_content = models.CharField(max_length = 50, choices = FEELINGS)
  grp_entity_ref = models.CharField(max_length = 50, choices = FEELINGS)
  taxonomy = models.CharField(max_length = 50, choices = FEELINGS)
  managing_content = models.CharField(max_length = 50, choices = FEELINGS)
  creating_dummy_content = models.CharField(max_length = 50, choices = FEELINGS)

  modify_display_content = models.CharField(max_length = 50, choices = FEELINGS)
  contents_using_view = models.CharField(max_length = 50, choices = FEELINGS)
  table_of_fields_with_views = models.CharField(max_length = 50, choices = FEELINGS)
  control_display_images = models.CharField(max_length = 50, choices = FEELINGS)
  adding_func = models.CharField(max_length = 50, choices = FEELINGS)
  finding_modules = models.CharField(max_length = 50, choices = FEELINGS)
  modifying_page_layout = models.CharField(max_length = 50, choices = FEELINGS)
  menu_endpoints = models.CharField(max_length = 50, choices = FEELINGS)
  styling_using_themes = models.CharField(max_length = 50, choices = FEELINGS)
  installig_ad_themes = models.CharField(max_length = 50, choices = FEELINGS)
  people_management = models.CharField(max_length = 50, choices = FEELINGS)
  site_management = models.CharField(max_length = 50, choices = FEELINGS)

  ws_quality = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  relevance = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  guidelines = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  overall_video_quality = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  text_readability = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  clarity_of_speech = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  visual_presentation = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  pace_of_tutorial = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  arrangement = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  network = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  installation_help = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  time_for_handson = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  experience_of_learning = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)
  overall_arrangement = models.CharField(max_length = 50, choices = RATE_SPOKEN_CHOICES)



  like_to_create_st = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  like_to_create_st_details = models.CharField(max_length = 300)
  num_of_experts_req = models.CharField(max_length = 50, choices = NUM_OF_EXPERTS)
  fees = models.CharField(max_length = 50, choices = FEES)


  like_abt_ws = models.CharField(max_length = 500)
  how_make_better = models.CharField(max_length = 500)
  experience = models.CharField(max_length = 500)
  suggestions = models.CharField(max_length = 500)

class LearnDrupalFeedback(models.Model):
  YES_NO_CHOICES =(
    ('','-----'), ('Yes', 'Yes'), ('No', 'No'),('NotApplicable ', 'Not Applicable '),
  )
  YES_NO = (
  ('','-----'), ('Yes', 'Yes'), ('No', 'No')
  )
  AGE =(
    ('','-----'),('below25', 'below 25'), ('25to34', '25 to 34'), ('35to44', '35 to 44'),('45to54', '45 to 54'),('55to64', '55 to 64'),('65andabove', '65 and above')
  )
  CURRENT_STATUS =(
  ('','-----'), ('Student', 'Student'), ('Individuallearner', 'Individual learner'), ('Workingprofessional', 'Working professional'), ('Teacher', 'Teacher'), ('Administrator', 'Administrator'), ('Others', 'Others')
  )
  PLAN_TO_CONDUCT = (
  ('','-----'), ('within3months', 'within 3 months'), ('within6months', 'within 6 months'), ('within1year', 'within 1 year'), ('notyetplanned', 'not yet planned')
  )
  LANGUAGE = (
  ('','-----'),('Hindi','Hindi'),('English','English'),('Marathi','Marathi'),('Urdu','Urdu'),('Kannanda','Kannanda'),('Bangali','Bangali'),('Malyalum','Malyalum'),('Tamil','Tamil'),('Telugu','Telugu'),('Oriya','Oriya'),('Assamese','Assamese'),('Gujrati','Gujrati'),
  )

  name = models.CharField(max_length = 100)
  phonemob = models.CharField(max_length = 100)
  email = models.EmailField(max_length = 100)
  affiliation = models.CharField(max_length = 100)
  place = models.CharField(max_length = 100)
  agegroup = models.CharField(max_length = 50, choices = AGE)
  currentstatus = models.CharField(max_length = 50, choices = CURRENT_STATUS)
  currentstatus_other = models.CharField(max_length = 50)
  is_drupal_in_curriculum = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  need_help_in_organizing = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  when_plan_to_conduct = models.CharField(max_length = 50, choices = PLAN_TO_CONDUCT)
  language = models.CharField(max_length = 50, choices = LANGUAGE)
  did_undergo_st_training = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  rate_spoken = models.CharField(max_length = 20)
  useful_for_placement = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  useful_for_placement_for_students = models.CharField(max_length = 50, choices = YES_NO_CHOICES)
  feedback = models.CharField(max_length = 500)
  like_to_learn_other_foss = models.CharField(max_length = 50, choices = YES_NO)
  mention_foss = models.CharField(max_length = 100)
  like_to_give_testimonial = models.CharField(max_length = 50, choices = YES_NO)
  testimonial = models.CharField(max_length = 100)

class InductionInterest(models.Model):
  YES_NO =(
    ('','-----'), ('Yes', 'Yes'), ('No', 'No'),
  )
  yes_option=(
    ('','-----'), ('Yes', 'Yes'),
    )
  GENDER_CHOICES =(
    ('', '-----'), ('Male', 'Male'), ('Female', 'Female'),
  )
  languages = (
    ('', '-----'), ('Assamese','Assamese'), ('Bengali', 'Bengali'), ('Bhojpuri', 'Bhojpuri'), ('Bodo', 'Bodo'), ('English', 'English'), ('Gujarati', 'Gujarati'),
    ('Hindi', 'Hindi'), ('Kannada', 'Kannada'), ('Kashmiri', 'Kashmiri'), ('Khasi', 'Khasi'), ('Konkani', 'Konkani'), ('Maithili', 'Maithili'),
    ('Malayalam', 'Malayalam'), ('Manipuri', 'Manipuri'), ('Marathi', 'Marathi'), ('Nepali', 'Nepali'),('Oriya', 'Oriya'), ('Punjabi', 'Punjabi'),
    ('Rajasthani', 'Rajasthani'), ('Sanskrit', 'Sanskrit'), ('Santhali', 'Santhali'), ('Sindhi', 'Sindhi'), ('Tamil', 'Tamil'), ('Telugu', 'Telugu'),
    ('Urdu', 'Urdu'), ('Other', 'Other'),
  )
  AGE =(
    ('','-----'),('20to25', '20 to 25 years'), ('26to30', '26 to 30 years'),('31to35', '31 to 35 years'),('35andabove', 'Above 35 years')
  )
  specialisation =(
     ('','-----'),('Arts', 'Arts'),('Science', 'Science'),('Commerce', 'Commerce'),
     ('EngineeringorComputerScience ', 'Engineering or Computer Science'),('Management', 'Management'), 
     ('Other', 'Other'),
    )
  education =(
    ('','-----'), ('3yeargraduatedegree(BABScB.Cometc)','3 year graduate degree (BA, BSc, B.Com, etc.)'),
    ('Professionaldegree(BEBTechetc)', 'Professional degree (BE, B.Tech, etc.)'),
    ('2yearMasters(MAMScMCometc)', '2 year Masters (MA, MSc, MCom, etc.)'),
    ('2yearprofessionalMasters(MEMTechMBAMPhiletc)', '2 year professional Masters (ME, MTech, MBA, MPhil, etc.)'),
    ('PhD', 'PhD'),
    ('Other','Other'),
    )
  designation = (
    ('','-----'),
    ('Lecturer','Lecturer'),
    ('AssistantProfessor','Assistant Professor'),
    ('AssociateProfessor','Associate Professor'),
    ('Professor','Professor'),
    ('Other','Other'),
    )
  years_of_experience = (
    ('','-----'),
    ('Lessthan1year','Less than 1 year'),
    ('Morethan1yearbutlessthan2years','More than 1 year, but less than 2 years'),
    ('Morethan2yearsbutlessthan5years','More than 2 years but less than 5 years'),
    ('Morethan5years','More than 5 years'),
    )

  email = models.EmailField(max_length = 100)
  name = models.CharField(max_length = 100)
  phonemob = models.CharField(max_length = 100)  
  age = models.CharField(max_length = 100, choices = AGE)
  gender = models.CharField(max_length = 50, choices = GENDER_CHOICES)
  mother_tongue = models.CharField(max_length = 100, choices = languages)
  other_language = models.CharField(max_length = 100)

  medium_of_studies = models.CharField(max_length = 100, choices = languages)
  other_medium = models.CharField(max_length = 100)

  education = models.CharField(max_length = 100, choices = education)
  other_education = models.CharField(max_length = 100)

  specialisation = models.CharField(max_length = 100, choices = specialisation)
  other_specialisation = models.CharField(max_length = 100)

  designation = models.CharField(max_length = 100, choices = designation)
  other_designation = models.CharField(max_length = 100)

  college = models.CharField(max_length = 100)
  college_address = models.CharField(max_length = 500)
  state = models.ForeignKey(State, on_delete=models.PROTECT )
  city = models.CharField(max_length = 100)
  pincode = models.PositiveIntegerField()
  experience_in_college = models.CharField(max_length = 100, choices = years_of_experience)
  
  bring_laptop = models.CharField(max_length = 50, choices = YES_NO)
  borrow_laptop = models.CharField(max_length = 50, choices = YES_NO)
  
  do_agree = models.CharField(max_length = 50, choices = yes_option)  
  no_objection = models.CharField(max_length = 50, choices = yes_option)
  other_comments = models.CharField(max_length = 500)

  class Meta(object):
    ordering = ('city',)

class InductionFinalList(models.Model):
  email = models.EmailField(max_length = 200)
  eoi_id = models.ForeignKey(InductionInterest, default=None, on_delete=models.PROTECT )
  code = models.CharField(max_length=255, default=None)
  # batch_code should be in form of year+month+batch_number e.g. 20171101 = [year 2017,month 11, batch 01]
  batch_code = models.PositiveIntegerField()
  created = models.DateTimeField(auto_now_add = True)

class Drupal2018_email(models.Model):
  email = models.EmailField(max_length = 200)

class MumbaiStudents(models.Model):
  stuid = models.ForeignKey('Student', on_delete=models.PROTECT )
  bid = models.ForeignKey('StudentBatch', on_delete=models.PROTECT )

class PaymentDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    academic_id = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
    academic_year = models.PositiveIntegerField()
    amount = models.CharField(max_length=20)
    purpose = models.CharField(max_length=20, null=True)
    status = models.PositiveIntegerField()
    description = models.CharField(max_length=20, null=True)
    gstno = models.CharField(max_length=15,null=True)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now_add = True) 
    
    class Meta(object):
      unique_together = ('academic_id','academic_year',)

class PaymentTransactionDetails(models.Model):
    paymentdetail = models.ForeignKey(PaymentDetails, on_delete=models.PROTECT )
    requestType = models.CharField(max_length=2)
    userId = models.ForeignKey(User, on_delete=models.PROTECT )
    amount = models.CharField(max_length=20)
    reqId = models.CharField(max_length=50)
    transId = models.CharField(max_length=100)
    refNo = models.CharField(max_length=50)
    provId = models.CharField(max_length=50)
    status = models.CharField(max_length=2)
    msg = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now_add = True)


class topperlist(models.Model):
  emailid = models.EmailField(max_length = 100)
  userid = models.PositiveIntegerField()
