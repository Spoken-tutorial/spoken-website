from django.db import models

#import auth user models
from django.contrib.auth.models import User

#creation app models
from creation.models import Foss_Category, Language

#validation
from django.core.exceptions import ValidationError

# Create your models here.
class State(models.Model):
	users = models.ManyToManyField(User, through='Resource_person')
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
	

class Resource_person(models.Model):
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
		
class Institute_type(models.Model):
	name = models.CharField(max_length=200)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	
	def __unicode__(self):
		return self.name

class Academic_center(models.Model):
	user = models.ForeignKey(User)
	state = models.ForeignKey(State)
	university = models.ForeignKey(University)
	academic_code = models.CharField(max_length=100, unique = True)
	institution_type = models.ForeignKey(Institute_type)
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

class Organiser(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	appoved_by = models.ForeignKey(User, related_name = 'organiser_approved_by')
	academic = models.ForeignKey(Academic_center)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

class Invigilator(models.Model):
	user = models.ForeignKey(User)
	appoved_by = models.ForeignKey(User, related_name = 'invigilator_approved_by')
	academic = models.ForeignKey(Academic_center)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

class Workshop(models.Model):
	organiser = models.ForeignKey(User)
	appoved_by = models.ForeignKey(User, related_name = 'workshop_approved_by')
	academic_center = models.ForeignKey(Academic_center)
	language = models.ForeignKey(Language)
	foss = models.ForeignKey(Foss_Category)
	workshop_code = models.CharField(max_length=100)
	workshop_date = models.DateTimeField()
	skype = models.BooleanField()
	status = models.PositiveSmallIntegerField()
	participant_counts = models.PositiveIntegerField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

class Test(models.Model):
	organiser = models.ForeignKey(User, related_name = 'origaniser')
	appoved_by = models.ForeignKey(User, related_name = 'test_approved_by')
	invigilator = models.ForeignKey(User)
	academic_center = models.ForeignKey(Academic_center)
	workshop = models.ForeignKey(Workshop)
	foss = models.ForeignKey(Foss_Category)
	test_code = models.CharField(max_length=100)
	test_date = models.DateTimeField()
	status = models.PositiveSmallIntegerField()
	participant_count = models.PositiveIntegerField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)
	
	
#need to delete
class Error(models.Model):
	name = models.CharField(max_length=200)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

