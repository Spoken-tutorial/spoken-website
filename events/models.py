from django.db import models

#import auth user models
from django.contrib.auth.models import User

#creation app models
from creation.models import Foss_Category, Language

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
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	
	def __unicode__(self):
		return self.name

	class Meta:
		unique_together = (("code","name"),)

class District(models.Model):
	state = models.ForeignKey(State)
	code = models.CharField(max_length=3)
	name = models.CharField(max_length=200)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	
	def __unicode__(self):
		return self.name
		
	class Meta:
		unique_together = (("state", "code","name"),)
		#unique_together = (("state_id","name"),)

class City(models.Model):
	state = models.ForeignKey(State)
	name = models.CharField(max_length=200)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	
	def __unicode__(self):
		return self.name
	
	class Meta:
		unique_together = (("name","state"),)

class Location(models.Model):
	district = models.ForeignKey(District)
	name = models.CharField(max_length=200)
	pincode = models.PositiveIntegerField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	
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
	foss = models.ForeignKey(Foss_Category)
	workshop_code = models.CharField(max_length=100, null=True)
	wdate = models.DateField()
	wtime = models.TimeField()
	skype = models.BooleanField()
	status = models.PositiveSmallIntegerField(default=0)
	participant_counts = models.PositiveIntegerField(default=0)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

class Test(models.Model):
	organiser = models.ForeignKey(User, related_name = 'test_organiser')
	appoved_by = models.ForeignKey(User, related_name = 'test_approved_by')
	invigilator = models.ForeignKey(User)
	academic = models.ForeignKey(AcademicCenter)
	workshop = models.ForeignKey(Workshop)
	foss = models.ForeignKey(Foss_Category)
	test_code = models.CharField(max_length=100)
	tdate = models.DateField()
	ttime = models.TimeField()
	status = models.PositiveSmallIntegerField()
	participant_count = models.PositiveIntegerField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	
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
