from django.db import models

#import auth user models
from django.contrib.auth.models import User

#creation app models
from creation.models import FossCategory, Language
from mdldjango.models import *

#validation
from django.core.exceptions import ValidationError

# Create your models here.
class State(models.Model):
    users = models.ManyToManyField(User, related_name="resource_person", through='ResourcePerson')
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=50)
    latitude = models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)
    longtitude = models.DecimalField(null=True, max_digits=10, decimal_places=4, blank=True)
    img_map_area = models.TextField()
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    
    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (("code","name"),)

class District(models.Model):
    state = models.ForeignKey(State)
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        unique_together = (("state", "code","name"),)
        #unique_together = (("state_id","name"),)

class City(models.Model):
    state = models.ForeignKey(State)
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        unique_together = (("name","state"),)

class Location(models.Model):
    district = models.ForeignKey(District)
    name = models.CharField(max_length=200)
    pincode = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add = True, null=True)
    updated = models.DateTimeField(auto_now = True, null=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        unique_together = (("name","district","pincode"),)
    

class ResourcePerson(models.Model):
    user = models.ForeignKey(User)
    state = models.ForeignKey(State)
    assigned_by = models.PositiveIntegerField()
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name = "Resource Person"
        unique_together = (("user","state"),)

class University(models.Model):
    name = models.CharField(max_length=200)
    state = models.ForeignKey(State)
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        unique_together = (("name","state"),)
        
class InstituteType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name

class AcademicCenter(models.Model):
    user = models.ForeignKey(User)
    state = models.ForeignKey(State)
    university = models.ForeignKey(University)
    academic_code = models.CharField(max_length=100, unique = True)
    institution_type = models.ForeignKey(InstituteType)
    institution_name = models.CharField(max_length=200, unique = True)
    district = models.ForeignKey(District)
    location = models.ForeignKey(Location)
    city = models.ForeignKey(City)
    street = models.CharField(max_length = 200)
    pincode = models.PositiveIntegerField()
    resource_center = models.BooleanField()
    rating = models.PositiveSmallIntegerField()
    contact_person = models.TextField()
    remarks = models.TextField()
    status = models.BooleanField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    class Meta:
        verbose_name = "Academic Center"
        unique_together = (("institution_name","district"), ("institution_name","university"))
        
    def __unicode__(self):
        return self.institution_name
        
class Organiser(models.Model):
    user = models.OneToOneField(User, related_name = 'organiser')
    appoved_by = models.ForeignKey(User, related_name = 'organiser_approved_by', blank=True, null=True)
    academic = models.ForeignKey(AcademicCenter, blank=True, null=True)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

class Invigilator(models.Model):
    user = models.OneToOneField(User)
    appoved_by = models.ForeignKey(User, related_name = 'invigilator_approved_by', blank=True, null=True)
    academic = models.ForeignKey(AcademicCenter)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

class Department(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
    def __unicode__(self):
        return self.name
        
class Workshop(models.Model):
    organiser = models.ForeignKey(User)
    appoved_by = models.ForeignKey(User, related_name = 'workshop_approved_by', null=True)
    academic = models.ForeignKey(AcademicCenter)
    department = models.ManyToManyField(Department)
    language = models.ForeignKey(Language)
    foss = models.ForeignKey(FossCategory)
    workshop_code = models.CharField(max_length=100, null=True)
    wdate = models.DateField()
    wtime = models.TimeField()
    skype = models.BooleanField()
    status = models.PositiveSmallIntegerField(default=0)
    participant_counts = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = (("organiser", "academic", "foss", "wdate", "wtime"),)

class Test(models.Model):
    organiser = models.ForeignKey(User, related_name = 'test_organiser')
    appoved_by = models.ForeignKey(User, related_name = 'test_approved_by', null=True)
    invigilator = models.ForeignKey(User)
    academic = models.ForeignKey(AcademicCenter)
    department = models.ManyToManyField(Department)
    workshop = models.ForeignKey(Workshop)
    foss = models.ForeignKey(FossCategory)
    test_code = models.CharField(max_length=100)
    tdate = models.DateField()
    ttime = models.TimeField()
    status = models.PositiveSmallIntegerField(default=0)
    participant_count = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = (("organiser", "academic", "foss", "tdate", "ttime"),)

class TestAttendance(models.Model):
    test = models.ForeignKey(Test)
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
    class Meta:
        verbose_name = "Test Attendance"
        unique_together = (("test", "mdluser_id"))

class PermissionType(models.Model):
    name = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    def __unicode__(self):
        return self.name
        
class Permission(models.Model):
    permissiontype = models.ForeignKey(PermissionType)
    user = models.ForeignKey(User, related_name = 'permission_user')
    state = models.ForeignKey(State, related_name = 'permission_state')
    district = models.ForeignKey(District, related_name = 'permission_district', null=True)
    university = models.ForeignKey(University, related_name = 'permission_iniversity', null=True)
    institute_type = models.ForeignKey(InstituteType, related_name = 'permission_institution_type', null=True)
    institute = models.ForeignKey(AcademicCenter, related_name = 'permission_district', null=True)
    assigned_by = models.ForeignKey(User, related_name = 'permission_assigned_by')
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    
class WorkshopAttendance(models.Model):
    workshop = models.ForeignKey(Workshop)
    mdluser_id = models.PositiveIntegerField()
    #mdluser = models.ForeignKey(MdlUser)
    password = models.CharField(max_length = 100, null=True)
    count = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name = "Workshop Attendance"
        unique_together = (("workshop", "mdluser_id"))
        #unique_together = (("workshop", "mdluser"))

class FossMdlCourses(models.Model):
    foss = models.ForeignKey(FossCategory)
    mdlcourse_id = models.PositiveIntegerField()
    mdlquiz_id = models.PositiveIntegerField()

class WorkshopLog(models.Model):
    user = models.ForeignKey(User)
    workshop = models.ForeignKey(Workshop)
    role = models.PositiveSmallIntegerField() #{0:'organiser', 1:'ResourcePerson', 2: 'Event Manager'}
    status = models.PositiveSmallIntegerField() #{0:'new', 1:'approved', 2:'completed', 3: 'rejected', 4:'update',  5:'Offline-Attendance submited', 6:'Marked Attendance'}
    created = models.DateTimeField(auto_now_add = True)

class TestLog(models.Model):
    user = models.ForeignKey(User)
    test = models.ForeignKey(Test)
    role = models.PositiveSmallIntegerField(default=0) #{0:'organiser', 1:'invigilator', 2:'ResourcePerson', 3: 'Event Manager'}
    status = models.PositiveSmallIntegerField(default=0) #{0:'new', 1:'RP-approved', 2:'Inv-approved', 3: 'ongoing', 4:'completed', 5:'Rp-rejected', 6:'Inv-rejected', 7:'Update', 8:'Attendance submited', 9:'Marked Attendance'}
    created = models.DateTimeField(auto_now_add = True)

class EventsNotification(models.Model):
    user = models.ForeignKey(User)
    role = models.PositiveSmallIntegerField(default=0) #{0:'organiser', 1:'invigilator', 2:'ResourcePerson', 3: 'Event Manager'}
    category = models.PositiveSmallIntegerField(default=0) #{'workshop', 'test', 'training'}
    categoryid = models.PositiveIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0) #{0:'new', 1:'update', 2:'approved', 3:'attendance', 4: 'completed', 5:'rejected'}
    message = models.CharField(max_length = 255)
    created = models.DateTimeField(auto_now_add = True)

class Training(models.Model):
    organiser = models.ForeignKey(User)
    appoved_by = models.ForeignKey(User, related_name = 'training_approved_by', null=True)
    academic = models.ForeignKey(AcademicCenter)
    department = models.ManyToManyField(Department)
    language = models.ForeignKey(Language)
    foss = models.ForeignKey(FossCategory)
    training_code = models.CharField(max_length=100, null=True)
    trdate = models.DateField()
    trtime = models.TimeField()
    skype = models.BooleanField()
    status = models.PositiveSmallIntegerField(default=0)
    participant_counts = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        unique_together = (("organiser", "academic", "foss", "trdate", "trtime"),)

class TrainingAttendance(models.Model):
    training = models.ForeignKey(Training)
    mdluser_id = models.PositiveIntegerField()
    #mdluser = models.ForeignKey(MdlUser)
    password = models.CharField(max_length = 100, null=True)
    count = models.PositiveSmallIntegerField(default=0)
    status = models.PositiveSmallIntegerField(default=0)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    class Meta:
        verbose_name = "Training Attendance"
        unique_together = (("training", "mdluser_id"))
        #unique_together = (("workshop", "mdluser"))
        
class TrainingLog(models.Model):
    user = models.ForeignKey(User)
    training = models.ForeignKey(Training)
    role = models.PositiveSmallIntegerField() #{0:'organiser', 1:'ResourcePerson', 2: 'Event Manager'}
    status = models.PositiveSmallIntegerField() #{0:'new', 1:'approved', 2:'completed', 3: 'rejected', 4:'update',  5:'Offline-Attendance submited', 6:'Marked Attendance'}
    created = models.DateTimeField(auto_now_add = True)
