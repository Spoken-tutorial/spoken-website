# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Standard Library
from datetime import date, datetime, timedelta

# Third Party Stuff
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
from django.db.models import Q, Sum
from django.db.models.signals import pre_delete

# Spoken Tutorial Stuff
from creation.models import FossAvailableForTest, FossCategory, Language
from events.signals import revoke_student_permission
from mdldjango.models import *


class State(models.Model):
    users = models.ManyToManyField(User, related_name="resource_person", through='ResourcePerson')
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=100)
    latitude = models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)
    longtitude = models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)
    img_map_area = models.TextField()
    has_map = models.BooleanField(default=1)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("code", "name"),)


class District(models.Model):
    state = models.ForeignKey(State)
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("state", "code", "name"),)


class City(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("name", "state"),)


class Location(models.Model):
    district = models.ForeignKey(District)
    name = models.CharField(max_length=200)
    pincode = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("name", "district", "pincode"),)


class ResourcePerson(models.Model):
    user = models.ForeignKey(User)
    state = models.ForeignKey(State)
    assigned_by = models.PositiveIntegerField()
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Resource Person"
        unique_together = (("user", "state"),)


class University(models.Model):
    name = models.CharField(max_length=200)
    state = models.ForeignKey(State)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("name", "state"),)


class InstituteCategory(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = "Institute Categorie"


class InstituteType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("name"),)


class AcademicCenter(models.Model):
    user = models.ForeignKey(User)
    state = models.ForeignKey(State)
    institution_type = models.ForeignKey(InstituteType)
    institute_category = models.ForeignKey(InstituteCategory)
    university = models.ForeignKey(University)
    academic_code = models.CharField(max_length=100, unique=True)
    institution_name = models.CharField(max_length=200)
    district = models.ForeignKey(District)
    location = models.ForeignKey(Location, null=True)
    city = models.ForeignKey(City)
    address = models.TextField()
    pincode = models.PositiveIntegerField()
    resource_center = models.BooleanField()
    rating = models.PositiveSmallIntegerField()
    contact_person = models.TextField()
    remarks = models.TextField()
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Academic Center"

    def __unicode__(self):
        return self.institution_name

    def get_training_count(self):
        qs = TrainingRequest.objects.filter(training_planner__academic_id=self.id, participants__gt=0,
                                            sem_start_date__lte=timezone.now())
        return qs.count()

    def get_training_participant_count(self):
        training = TrainingRequest.objects.filter(training_planner__academic_id=self.id, participants__gt=0,
                                                  sem_start_date__lte=timezone.now()).aggregate(Sum('participants'))
        return training['participants__sum']


class Organiser(models.Model):
    user = models.OneToOneField(User, related_name='organiser')
    appoved_by = models.ForeignKey(User, related_name='organiser_approved_by', blank=True, null=True)
    academic = models.ForeignKey(AcademicCenter, blank=True, null=True)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username


class Invigilator(models.Model):
    user = models.OneToOneField(User)
    appoved_by = models.ForeignKey(User, related_name='invigilator_approved_by', blank=True, null=True)
    academic = models.ForeignKey(AcademicCenter)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user.username


class Department(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Course(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("name"),)


class TrainingExtraFields(models.Model):
    paper_name = models.CharField(max_length=200)
    approximate_hour = models.PositiveIntegerField(default=0)
    online_test = models.PositiveIntegerField(default=0)
    is_tutorial_useful = models.BooleanField(default=0)
    future_training = models.BooleanField(default=0)
    recommend_to_others = models.BooleanField(default=0)
    no_of_lab_session = models.CharField(max_length=30, null=True)


class Training(models.Model):
    organiser = models.ForeignKey(Organiser)
    appoved_by = models.ForeignKey(User, related_name='training_approved_by', null=True)
    academic = models.ForeignKey(AcademicCenter)
    course = models.ForeignKey(Course)
    training_type = models.PositiveIntegerField(default=0)
    training_code = models.CharField(max_length=100, null=True)
    department = models.ManyToManyField(Department)
    language = models.ForeignKey(Language)
    foss = models.ForeignKey(FossCategory)
    tdate = models.DateField()
    ttime = models.TimeField()
    skype = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    # 0:request done, 1: attendance submit, 2: training manger approved,
    # 3: mark attenda done, 4: complete, 5: rejected
    extra_fields = models.OneToOneField(TrainingExtraFields, null=True)
    participant_count = models.PositiveIntegerField(default=0)
    trusted = models.BooleanField(default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("organiser", "academic", "foss", "tdate", "ttime"),)


class TrainingAttendance(models.Model):
    training = models.ForeignKey(Training)
    mdluser_id = models.PositiveIntegerField(null=True, blank=True)
    firstname = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=10, null=True)
    email = models.EmailField(null=True)
    password = models.CharField(max_length=100, null=True)
    count = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Training Attendance"


class TrainingLog(models.Model):
    user = models.ForeignKey(User)
    training = models.ForeignKey(Training)
    academic = models.ForeignKey(AcademicCenter)
    role = models.PositiveSmallIntegerField()
    # {0:'organiser', 1:'ResourcePerson', 2: 'Event Manager'}
    status = models.PositiveSmallIntegerField()
    # {0:'new', 1:'approved', 2:'completed', 3: 'rejected', 4:'update',
    # 5:'Offline-Attendance submited', 6:'Marked Attendance'}
    created = models.DateTimeField(auto_now_add=True)


class TestCategory(models.Model):
    name = models.CharField(max_length=200)
    status = models.BooleanField(default=0)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)

    def __unicode__(self):
        return self.name


class Test(models.Model):
    organiser = models.ForeignKey(Organiser, related_name='test_organiser')
    test_category = models.ForeignKey(TestCategory, related_name='test_category')
    appoved_by = models.ForeignKey(User, related_name='test_approved_by', null=True)
    invigilator = models.ForeignKey(Invigilator, related_name='test_invigilator', null=True)
    academic = models.ForeignKey(AcademicCenter)
    department = models.ManyToManyField(Department)
    training = models.ForeignKey('TrainingRequest', null=True)
    foss = models.ForeignKey(FossCategory)
    test_code = models.CharField(max_length=100)
    tdate = models.DateField()
    ttime = models.TimeField()
    status = models.PositiveSmallIntegerField(default=0)
    participant_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Test Categorie"
        unique_together = (("organiser", "academic", "foss", "tdate", "ttime"),)

    def get_test_attendance_count(self):
        return TestAttendance.objects.filter(test_id=self.id, status__gte=2).count()

    def update_test_participant_count(self):
        self.participant_count = self.get_test_attendance_count()
        self.save()
        return self


class TestAttendance(models.Model):
    test = models.ForeignKey(Test)
    student = models.ForeignKey('Student', null=True)
    mdluser_firstname = models.CharField(max_length=100)
    mdluser_lastname = models.CharField(max_length=100)
    mdluser_id = models.PositiveIntegerField()
    mdlcourse_id = models.PositiveIntegerField(default=0)
    mdlquiz_id = models.PositiveIntegerField(default=0)
    mdlattempt_id = models.PositiveIntegerField(default=0)
    password = models.CharField(max_length=100, null=True)
    count = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Test Attendance"
        unique_together = (("test", "mdluser_id"))


class TestLog(models.Model):
    user = models.ForeignKey(User)
    test = models.ForeignKey(Test)
    academic = models.ForeignKey(AcademicCenter)
    role = models.PositiveSmallIntegerField(default=0)
    # {0:'organiser', 1:'invigilator', 2:'ResourcePerson', 3: 'Event Manager'}
    status = models.PositiveSmallIntegerField(default=0)
    # {0:'new', 1:'RP-approved', 2:'Inv-approved', 3: 'ongoing', 4:'completed',
    # 5:'Rp-rejected', 6:'Inv-rejected', 7:'Update',
    # 8:'Attendance submited', 9:'Marked Attendance'}
    created = models.DateTimeField(auto_now_add=True)


class PermissionType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class Permission(models.Model):
    permissiontype = models.ForeignKey(PermissionType)
    user = models.ForeignKey(User, related_name='permission_user')
    state = models.ForeignKey(State, related_name='permission_state')
    district = models.ForeignKey(District, related_name='permission_district', null=True)
    university = models.ForeignKey(University, related_name='permission_iniversity', null=True)
    institute_type = models.ForeignKey(InstituteType, related_name='permission_institution_type', null=True)
    institute = models.ForeignKey(AcademicCenter, related_name='permission_district', null=True)
    assigned_by = models.ForeignKey(User, related_name='permission_assigned_by')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class FossMdlCourses(models.Model):
    foss = models.ForeignKey(FossCategory)
    mdlcourse_id = models.PositiveIntegerField()
    mdlquiz_id = models.PositiveIntegerField()


class EventsNotification(models.Model):
    user = models.ForeignKey(User)
    role = models.PositiveSmallIntegerField(default=0)
    # {0:'organiser', 1:'invigilator', 2:'ResourcePerson', 3: 'Event Manager'}
    academic = models.ForeignKey(AcademicCenter)
    category = models.PositiveSmallIntegerField(default=0)
    # {'workshop', 'training', 'test'}
    categoryid = models.PositiveIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    # {0:'new', 1:'update', 2:'approved', 3:'attendance',
    # 4: 'completed', 5:'rejected'}
    message = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True)


class Testimonials(models.Model):
    user = models.ForeignKey(User, related_name='testimonial_created_by')
    approved_by = models.ForeignKey(User, related_name='testimonial_approved_by', null=True)
    user_name = models.CharField(max_length=200)
    actual_content = models.TextField()
    minified_content = models.TextField()
    short_description = models.TextField()
    source_title = models.CharField(max_length=200, null=True)
    source_link = models.URLField(null=True)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True, null=True)


class OrganiserNotification(models.Model):
    user = models.ForeignKey(User)


# EVENTS VERSION 2 MODELS
# -----------------------------------------------------------------------------
class Student(models.Model):
    user = models.OneToOneField(User)
    gender = models.CharField(max_length=15)
    verified = models.PositiveSmallIntegerField(default=0)
    error = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
    year = models.PositiveIntegerField()  # 2010-2014
    stcount = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("academic", "year", "department")

    def __unicode__(self):
        return '%s, %s Batch' % (self.department.name, self.year)

    def get_batch_info(self):
        return '%s, %s, %s Batch' % (self.academic, self.department.name, self.year)

    def student_count(self):
        return StudentMaster.objects.filter(batch_id=self.id).count()

    def can_add_student(self, organiser_id):
        organiser = Organiser.objects.get(pk=organiser_id)
        if self.organiser.academic_id == organiser.academic_id:
            return True
        return False

    def update_student_count(self):
        self.stcount = StudentMaster.objects.filter(batch_id=self.id).count()
        self.save()
        return self.stcount

    def is_foss_batch_acceptable(self, course_id):
        sm = StudentMaster.objects.filter(batch_id=self.id)
        for s in sm:
            if not TrainingAttend.objects.filter(student_id=s.student_id, training__course_id=course_id).exists():
                return True
        return False

    def has_training(self):
        if self.trainingrequest_set.exists():
            return False
        return True


class StudentMaster(models.Model):
    batch = models.ForeignKey(StudentBatch)
    student = models.ForeignKey(Student)
    moved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("batch", "student")
        ordering = ["student__user__first_name"]


class Semester(models.Model):
    name = models.CharField(max_length=50)
    even = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name


class LabCourse(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name


class CourseMap(models.Model):
    # name = models.CharField(max_length=200, null=True, blank=True)
    course = models.ForeignKey(LabCourse, null=True, blank=True)
    foss = models.ForeignKey(FossCategory)
    test = models.BooleanField(default=False)
    # {0 => one day workshop, 1 => mapped course, 2 => unmapped course}
    category = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        if self.course_id:
            return '%s (%s)' % (self.foss.foss, self.course.name)
        return self.foss.foss

    def course_name(self):
        if self.course_id:
            return '%s - %s' % (self.course.name, self.foss.foss)
        return self.foss

    def category_name(self):
        courses = {
            0: 'Software Course outside lab hours',
            1: 'Software Course mapped in lab hours',
            2: 'Software Course unmapped in lab hours',
            3: 'EduEasy Software',
            4: 'other'
        }
        return courses[self.category]

    class Meta:
        unique_together = ("course", "foss", "category")
        ordering = ('foss',)


class TrainingPlanner(models.Model):
    year = models.CharField(max_length=50)
    academic = models.ForeignKey(AcademicCenter)
    organiser = models.ForeignKey(Organiser)
    semester = models.ForeignKey(Semester)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.semester.name

    def training_requests(self):
        return TrainingRequest.objects.filter(
            training_planner_id=self.id
        ).exclude(Q(participants=0) & Q(status=1))

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
            ctp = TrainingPlanner.objects.get(year=year, semester=sem, organiser=self.organiser, academic=self.academic)
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
        now = timezone.now()
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
        if self.training_requests().filter(department_id=department_id, batch_id=batch_id).count() > 2:
            return True
        return False

    def is_school_full(self, department_id, batch_id):
        if self.training_requests().filter(department_id=department_id, batch_id=batch_id).count() > 11:
            return True
        return False

    # todo with test without test
    def is_course_full(self, category, department_id, batch_id):
        if self.training_requests().filter(department_id=department_id, batch_id=batch_id,
                                           course__category=category, course__test=True).count() > 1:
            return True
        elif self.training_requests().filter(department_id=department_id, batch_id=batch_id,
                                             course__category=category, course__test=False).count() > 2:
            return True
        return False

    def is_school_course_full(self, category, department_id, batch_id):
        if self.training_requests().filter(department_id=department_id, batch_id=batch_id,
                                           course__category=category, course__test=True).count() > 1:
            return True
        elif self.training_requests().filter(department_id=department_id, batch_id=batch_id,
                                             course__category=category, course__test=False).count() > 11:
            return True
        return False

    def is_unmapped_course_full(self, department_id):
        if self.training_requests().filter(department_id=department_id, course__category=2).count() > 4:
            return True
        return False

    def get_current_semester_date_duration(self):
        if self.semester.even:
            return datetime.strptime(
                str(int(self.year) + 1) + '-01-01', '%Y-%m-%d'
            ).date(), datetime.strptime(
                str(int(self.year) + 1) + '-06-30', '%Y-%m-%d'
            ).date()
        return datetime.strptime(
            str(self.year) + '-07-01', '%Y-%m-%d'
        ).date(), datetime.strptime(
            str(self.year) + '-12-31', '%Y-%m-%d'
        ).date()

    def get_current_semester_date_duration_new(self):
        if self.semester.even:
            return datetime.strptime(
                str(int(self.year) + 1) + '-01-01', '%Y-%m-%d'
            ).date(), datetime.strptime(
                str(int(self.year) + 1) + '-03-31', '%Y-%m-%d'
            ).date()
        return datetime.strptime(
            str(self.year) + '-07-01', '%Y-%m-%d'
        ).date(), datetime.strptime(
            str(self.year) + '-9-30', '%Y-%m-%d'
        ).date()

    class Meta:
        unique_together = ("year", "academic", "organiser", "semester")


class TestTrainingManager(models.Manager):

    def get_queryset(self):
        return super(TestTrainingManager, self).get_queryset().filter(
            (
                Q(course__category=0) &
                # Q(status=1) &
                Q(sem_start_date__lte=timezone.now() - timedelta(days=15))
            ) |
            (
                Q(course__category__gt=0) &
                Q(sem_start_date__lte=timezone.now() - timedelta(days=30))
            ),
            participants__gt=0
        ).order_by('-training_planner__year', '-training_planner__semester_id')


class TrainingRequest(models.Model):
    training_planner = models.ForeignKey(TrainingPlanner)
    department = models.ForeignKey(Department)
    sem_start_date = models.DateField()
    course = models.ForeignKey(CourseMap)
    batch = models.ForeignKey(StudentBatch, null=True)
    participants = models.PositiveIntegerField(default=0)
    # status = models.BooleanField(default=False)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # created = models.DateTimeField()
    # updated = models.DateTimeField()

    # managers
    objects = models.Manager()  # The default manager.
    test_training = TestTrainingManager()

    # return course type
    def get_course_type(self):
        if self.course.category == 0:
            return 'Outside Lab Hours'
        elif self.course.category == 1:
            return 'Mapped Course'
        elif self.course.category == 2:
            return 'Unmapped Course'
        return ''

    def is_training_certificate_allowed(self):
        if not FossAvailableForTest.objects.filter(foss=self.course.foss, foss__status=True).count():
            return True
        return False

    # restrict the month to rise a training request
    def can_mark_attendance(self):
        sem_start, sem_end = self.training_planner.get_current_semester_date_duration()
        today = date.today()
        if self.status == 1 or today < self.sem_start_date or today > sem_end:
            return False
        # elif self.course.category == 0 and date.today() > self.sem_start_date:
            # return False
        return True

    def update_participants_count(self):
        self.participants = TrainingAttend.objects.filter(training_id=self.id).count()
        self.save()
        return self.participants

    def get_partipants_from_attendance(self):
        return TrainingAttend.objects.filter(training_id=self.id).count()

    def get_partipants_from_batch(self):
        if self.batch:
            return self.batch.stcount
        return 0

    def attendance_summery(self):
        if self.status == 1:
            return self.participants
        training_attend_count = TrainingAttend.objects.filter(training_id=self.id).count()
        student_master_count = StudentMaster.objects.filter(batch_id=self.batch_id).count()
        return '(%d / %d)' % (training_attend_count, student_master_count)

    def can_edit(self):
        if self.status == 1 or TrainingAttend.objects.filter(training_id=self.id).exists():
            return False
        return True

    def training_name(self):
        if self.batch:
            return 'WC-%d, %s, %s - %s - %s' % (self.id, self.course, self.batch,
                                                self.training_planner.year, int(self.training_planner.year) + 1)
        return 'WC-%d, %s, %s - %s' % (self.id, self.course,
                                       self.training_planner.year, int(self.training_planner.year) + 1)


class TrainingAttend(models.Model):
    training = models.ForeignKey(TrainingRequest)
    student = models.ForeignKey(Student)
    language = models.ForeignKey(Language, default=None)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("training", "student")


class TrainingCertificate(models.Model):
    student = models.ForeignKey(Student)
    training = models.ForeignKey(TrainingRequest)
    password = models.CharField(max_length=255, null=True)
    count = models.PositiveSmallIntegerField(default=0)
    updated = models.DateTimeField()

    def __unicode__(self):
        return self.student


class TrainingFeedback(models.Model):
    training = models.ForeignKey(TrainingRequest)
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
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("training", "mdluser_id"))


class TrainingLanguageFeedback(models.Model):
    training = models.ForeignKey(TrainingRequest)
    mdluser_id = models.PositiveIntegerField()
    name = models.CharField(max_length=100, null=True, default=None)
    age = models.PositiveIntegerField()
    medium_of_instruction = models.PositiveIntegerField()
    gender = models.BooleanField()
    language_prefered = models.ForeignKey(Language, null=True)
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

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("training", "mdluser_id"))


# School, Live Workshop, Pilot Workshop
class SingleTraining(models.Model):
    organiser = models.ForeignKey(Organiser)
    state = models.ForeignKey(State, null=True)
    institution_type = models.ForeignKey(InstituteType, null=True)
    academic = models.ForeignKey(AcademicCenter)
    course = models.ForeignKey(CourseMap)  # type 0
    # {0:School, 3:Vocational, 1:Live Workshop, 2:Pilot Workshop}
    training_type = models.PositiveIntegerField(default=0)
    language = models.ForeignKey(Language)
    tdate = models.DateField()
    ttime = models.TimeField(null=True, blank=True)
    # {0:request done, 1: attendance submited, 2: completed}
    status = models.PositiveSmallIntegerField(default=0)
    participant_count = models.PositiveIntegerField(default=0)
    total_participant_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def is_singletraining_certificate_allowed(self):
        if not FossAvailableForTest.objects.filter(foss=self.course.foss, foss__status=True).count():
            return True
        return False

    class Meta:
        unique_together = (("organiser", "academic", "course", "tdate", "ttime"),)


class SingleTrainingAttendance(models.Model):
    training = models.ForeignKey(SingleTraining)
    foss = models.PositiveIntegerField(default=0)
    firstname = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=10, null=True)
    email = models.EmailField(null=True)
    password = models.CharField(max_length=100, null=True)
    count = models.PositiveSmallIntegerField(default=0)
    # {0:waiting for confirmation, 1:approved, 2:complete}
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (("training", "firstname", "lastname", "email"),)


class TrainingLiveFeedback(models.Model):
    training = models.ForeignKey(SingleTraining)

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
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("training", "email"))


# Signals
pre_delete.connect(revoke_student_permission, sender=Student)


class StudentStream(models.Model):
    STUDENT_STREAM_CHOICES = (
        ('0', 'Engineering'), ('1', 'Science'), ('2', 'Arts and Humanities'), ('3', 'Polytechnic/ Diploma programs'),
        ('4', 'Commerce and Business Studies'), ('5', 'ITI'), ('6', 'Other')
    )
    student_stream = models.CharField(max_length=50, choices=STUDENT_STREAM_CHOICES)

    def __unicode__(self):
        return self.student_stream


class HelpfulFor(models.Model):
    HELPFUL_FOR_CHOICES = (
        ('0', 'Academic Performance'),
        ('1', 'Project Assignments'),
        ('2', 'To get job interviews'),
        ('3', 'To get jobs'),
        ('4', 'All of the above')
    )
    helpful_for = models.CharField(max_length=50, choices=HELPFUL_FOR_CHOICES)

    def __unicode__(self):
        return self.helpful_for


class OrganiserFeedback(models.Model):
    IS_SPOKEN_HELPFUL_CHOICES = (('', '-----'),
                                 ('StronglyAgree', 'Strongly Agree'),
                                 ('Agree', 'Agree'),
                                 ('Neutral', 'Neutral'),
                                 ('Disagree', 'Disagree'),
                                 ('StronglyDisagree', 'Strongly Disagree'),
                                 ('Noidea', 'No idea'), )
    RATE_SPOKEN_CHOICES = (('', '-----'),
                           ('Excellent', 'Excellent'),
                           ('Good', 'Good'),
                           ('Fair', 'Fair'),
                           ('Bad', 'Bad'),
                           ('Verybad', 'Very bad'))
    YES_NO_CHOICES = (('', '-----'), ('Yes', 'Yes'), ('No', 'No'), )
    AGE_CHOICES = (('', '-----'), ('<25', '<25 years'), ('25-35', '25-35 years'), ('35+', '35 years and above'), )
    GENDER_CHOICES = (('', '-----'), ('Male', 'Male'), ('Female', 'Female'), )
    DESIGNATION_CHOICES = (
        ('', '-----'), ('Student', 'Student'), ('Faculty', 'Faculty'), ('Staff', 'Staff'), ('Admin', 'Admin'),
    )
    MEDIUM_OF_INSTRUCTION_CHOICES = (
        ('', '-----'), ('English', 'English'), ('Vernacular', 'Vernacular'), ('Mixed', 'Mixed'),
    )
    STUDENT_EDUCATION_LANGUAGE_CHOICES = (
        ('', '-----'), ('English', 'Mostly English'), ('Vernacular', 'Mostly Vernacular'), ('Mixed', 'Mostly Mixed')
    )
    STUDENT_GENDER_CHOICES = (('', '-----'), ('Male', 'Mostly Male'), ('Female', 'Mostly Female'), ('Mixed', 'Mixed'), )
    STUDENT_LOCATION_CHOICES = (
        ('', '-----'), ('Urban', 'Mainly Urban'), ('Rural', 'Mainly Rural'), ('Mixed', 'Mixed'), ('Notsure', 'Not sure')
    )
    DURATION_OF_TUTORIAL_CHOICES = (('', '-----'),
                                    ('<0.5', 'Less than 0.5 hour'),
                                    ('0.5-2', '0.5 - 2 hour'),
                                    ('2-10', '2-10 hours'),
                                    ('10+', 'Above 10 hours'),
                                    ('NA', 'Not applicable'), )
    SIDE_BY_SIDE_METHOD_IS_CHOICES = (('', '-----'),
                                      ('0', 'Explaining the video to a neighbor'),
                                      ('1', 'Waiting for mentors explanation'),
                                      ('2', 'Watching and practicing simultaneously'),
                                      ('3', 'Dont know what this method is'), )
    IN_SIDE_BY_SIDE_METHOD_CHOICES = (('', '-----'),
                                      ('0', 'The video has to be maximized'),
                                      ('1', 'The software has to be maximized'),
                                      ('2', 'Both software and video are maximized'),
                                      ('3', 'None of the above are maximized'), )
    GOOD_INVESTMENT_CHOICES = (('', '-----'), ('Yes', 'Yes'), ('No', 'No'), ('Notsure', 'Not sure'))

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    age = models.CharField(max_length=20, choices=AGE_CHOICES)
    state = models.ForeignKey(State)
    district = models.ForeignKey(District)
    city = models.ForeignKey(City)
    university = models.ForeignKey(AcademicCenter)
    designation = models.CharField(max_length=20, choices=DESIGNATION_CHOICES)
    medium_of_instruction = models.CharField(max_length=50, choices=MEDIUM_OF_INSTRUCTION_CHOICES)
    student_stream = models.ManyToManyField(StudentStream, related_name='events_StudentStream_related')
    student_education_language = models.CharField(max_length=50, choices=STUDENT_EDUCATION_LANGUAGE_CHOICES)
    student_gender = models.CharField(max_length=50, choices=STUDENT_GENDER_CHOICES)
    student_location = models.CharField(max_length=50, choices=STUDENT_LOCATION_CHOICES)
    offered_training_foss = models.ManyToManyField(FossCategory, related_name='events_FossCategory_related')
    duration_of_tutorial = models.CharField(max_length=50, choices=DURATION_OF_TUTORIAL_CHOICES)
    language = models.ManyToManyField(Language, related_name='events_Language_related')
    side_by_side_yes_no = models.CharField(max_length=50, choices=YES_NO_CHOICES)
    side_by_side_method_is = models.CharField(max_length=50, choices=SIDE_BY_SIDE_METHOD_IS_CHOICES)
    in_side_by_side_method = models.CharField(max_length=50, choices=IN_SIDE_BY_SIDE_METHOD_CHOICES)
    good_investment = models.CharField(max_length=50, choices=GOOD_INVESTMENT_CHOICES)
    helpful_for = models.ManyToManyField(HelpfulFor, related_name='events_HelpfulFor_related')
    is_comfortable_self_learning = models.CharField(max_length=50, choices=IS_SPOKEN_HELPFUL_CHOICES)
    is_classroom_better = models.CharField(max_length=50, choices=IS_SPOKEN_HELPFUL_CHOICES)
    is_student_expectations = models.CharField(max_length=50, choices=IS_SPOKEN_HELPFUL_CHOICES)
    is_help_get_interview = models.CharField(max_length=50, choices=IS_SPOKEN_HELPFUL_CHOICES)
    is_help_get_job = models.CharField(max_length=50, choices=IS_SPOKEN_HELPFUL_CHOICES)
    is_got_job = models.CharField(max_length=50, choices=IS_SPOKEN_HELPFUL_CHOICES)
    relevance = models.CharField(max_length=50, choices=RATE_SPOKEN_CHOICES)
    information_content = models.CharField(max_length=50, choices=RATE_SPOKEN_CHOICES)
    audio_video_quality = models.CharField(max_length=50, choices=RATE_SPOKEN_CHOICES)
    presentation_quality = models.CharField(max_length=50, choices=RATE_SPOKEN_CHOICES)
    overall_rating = models.CharField(max_length=50, choices=RATE_SPOKEN_CHOICES)
    trained_foss = models.ManyToManyField(FossCategory)
    is_training_benefited = models.CharField(max_length=50, choices=GOOD_INVESTMENT_CHOICES)
    testimonial = models.CharField(max_length=500)
    any_other_suggestions = models.CharField(max_length=500)
    can_contact = models.CharField(max_length=50, choices=YES_NO_CHOICES)


def get_email_dir(instance, filename):
    email_dir = instance.email.replace('.', '_')
    email_dir = email_dir.replace('@', 'on')
    return "latex/%s/%s" % (email_dir, filename)


class LatexWorkshopFileUpload(models.Model):
    email = models.EmailField()
    file_upload = models.FileField(upload_to=get_email_dir)
