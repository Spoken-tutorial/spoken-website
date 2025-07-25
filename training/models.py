from django.db import models
from builtins import str
from builtins import object

#import auth user models
from django.contrib.auth.models import User
from creation.models import FossCategory, Language
from events.models import *
from donate.models import Payee
from donate.helpers import GENDER_CHOICES
import json

EVENT_TYPE_CHOICES =(
	('', '-----'), ('FDP', 'Faculty Development Program (FDP)'), ('Workshop', 'Blended Mode Workshop'),('sdp', 'Student Training Programme'),('TPDP', 'Teachers Professional Development Program'
), ('SSDP', 'School Students  Development Program'), ('PDP', 'Professional Development Program'), ('CDP', 'Community Development Program'),
('HN', 'Health And Nutrition Program'), ('INTERN', 'Internship Programme'),
	)


REGISTRATION_TYPE_CHOICES =(
    ('', '-----'),  (1, 'Subscribed College'),(2, 'Manual Registration')
    )

class CompanyType(models.Model):
	name = models.CharField(max_length=250)

	def __str__(self):
		return self.name

class Company(models.Model):
	name = models.CharField(max_length=250)
	added_by = models.ForeignKey(User, on_delete=models.PROTECT)
	company_type = models.ForeignKey(CompanyType, on_delete=models.PROTECT, null=True, blank=True)
	state = models.ForeignKey(State, on_delete=models.PROTECT)
	district = models.ForeignKey(District, on_delete=models.PROTECT)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name_plural = "Companies"
		ordering = ['name']

	def __str__(self):
		return self.name


class ILWCourse(models.Model):
	name = models.CharField(max_length=255)
	foss = models.ManyToManyField(FossCategory, related_name='courses')

	def __str__(self):
		return self.name

class TrainingEvents(models.Model):
	event_type = models.CharField(max_length = 50, choices = EVENT_TYPE_CHOICES)
	event_fee = models.PositiveIntegerField(default=500)
	event_name = models.CharField(max_length=200)
	state = models.ForeignKey(State, on_delete=models.PROTECT )
	host_college = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
	foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT , null=True, blank=True )
	course = models.ForeignKey(ILWCourse, on_delete=models.PROTECT, null=True, blank=True )
	is_course = models.BooleanField(default=False) #True if the ILW consists of multiple foss packaged as a course
	Language_of_workshop = models.ForeignKey(Language, on_delete=models.PROTECT )
	event_start_date = models.DateField(default=datetime.now)
	event_end_date = models.DateField(default=datetime.now)
	event_coordinator_name =  models.CharField(max_length=200)
	event_coordinator_email = models.EmailField(null=True)
	event_coordinator_contact_no = models.CharField(max_length = 100, null=True)
	registartion_start_date = models.DateField(default=datetime.now)
	registartion_end_date = models.DateField(default=datetime.now)
	training_status = models.PositiveSmallIntegerField(default=0)
	entry_date = models.DateTimeField(auto_now_add = True)
	entry_user = models.ForeignKey(User, on_delete=models.PROTECT)
	company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True)
	city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True)
	payment_required = models.BooleanField(default=False)
	instructor_name = models.CharField(max_length=255, blank=True, null=True, default='') # For internship
	# False => Payment only from non-subscribed college organisers and students.
	# True  => Payment from ALL users, regardless of group or college payment status.


	def __str__(self):
		return self.event_name


class Participant(models.Model):
	name = models.CharField(max_length=255,null=True)
	email = models.EmailField(max_length=255,null=True)
	gender = models.CharField(choices=GENDER_CHOICES, max_length=6,null=True)
	amount = models.DecimalField(max_digits=10,decimal_places=2,null=True)	
	event = models.ForeignKey(TrainingEvents, on_delete=models.PROTECT)
	user = models.ForeignKey(User, on_delete=models.PROTECT)
	state = models.ForeignKey(State, on_delete=models.PROTECT )
	college = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT)
	department = models.ForeignKey(Department, on_delete=models.PROTECT, null=True)
	registartion_type = models.PositiveSmallIntegerField(choices= REGISTRATION_TYPE_CHOICES, default=1)
	created = models.DateTimeField(auto_now_add = True)
	foss_language = models.ForeignKey(Language, on_delete=models.PROTECT, null=True )
	language_hn = models.IntegerField( null=True, blank=True )
	payment_status = models.ForeignKey(Payee, on_delete=models.PROTECT, null=True)
	reg_approval_status = models.PositiveSmallIntegerField(default=0)
	company = models.ForeignKey(Company, on_delete=models.PROTECT, null=True, blank=True)
	city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True)
	source = models.CharField(max_length=25, null=True, default=None)

	@property
	def payment_status_message(self):
		ps = self.payment_status
		if not ps:
			return "CSV Upload"
		if ps:
			payee_status = ps.status # asc method
			transaction_status = ps.transaction.order_status if ps.transaction else "" #hdfc gateway

			if payee_status == 1 or transaction_status == "CHARGED":
				return "Payment successfully completed 1"
			if payee_status == 2 and transaction_status in ["FAILED", "AUTHENTICATION_FAILED", "AUTHORIZATION_FAILED"]:
				return "Payment failed 1"
			if payee_status == 0 :
				return "Payment Initiated, not paid 1"
		return "CSV Upload"
	
	class Meta(object):
		unique_together = ('event', 'user', 'payment_status')

	def get_foss_langs(self):
		selected_foss = {}
		event = TrainingEvents.objects.get(id=self.event.id)
		event_lang = str(event.Language_of_workshop.id)
		user_lang_id = str(self.foss_language.id) if self.foss_language else None
		languages = [[event_lang, user_lang_id], 0] if user_lang_id else [[event_lang], 0]
		for foss in event.course.foss.all():
			selected_foss[foss.id] = languages
		return json.dumps(selected_foss)


class EventAttendance(models.Model):
	participant = models.ForeignKey(Participant, on_delete=models.PROTECT)
	event = models.ForeignKey(TrainingEvents, on_delete=models.PROTECT)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)


class TrainingCertificate(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.PROTECT)
    serial_no = models.CharField(max_length=50)  # purpose+uin+1stletter
    counter = models.IntegerField()
    event = models.ForeignKey(TrainingEvents, on_delete=models.PROTECT)
    paper = models.CharField(max_length=100, null=True, blank=True)
    verified = models.IntegerField(default=0)
    serial_key = models.CharField(max_length=200, null=True)
    short_key = models.CharField(max_length=50, null=True)

class ILWFossMdlCourses(models.Model):
	foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT, related_name='eventfoss', null=True)
	mdlcourse_id = models.PositiveIntegerField()
	mdlquiz_id = models.PositiveIntegerField()
	testfoss = models.ForeignKey(FossCategory, on_delete=models.PROTECT, related_name='testfoss', null=True)
	class Meta(object):
		ordering = ['foss']


	def __str__(self):
		return self.foss.foss

class EventTestStatus(models.Model):
	participant = models.ForeignKey(Participant, on_delete=models.PROTECT)
	event = models.ForeignKey(TrainingEvents, on_delete=models.PROTECT)
	mdlemail = models.EmailField(max_length=255,null=True)
	fossid = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
	mdlcourse_id = models.PositiveIntegerField(default=0)
	mdlquiz_id = models.PositiveIntegerField(default=0)
	mdlattempt_id = models.PositiveIntegerField(default=0)
	part_status = models.PositiveSmallIntegerField(default=0)
	mdlgrade= models.DecimalField(max_digits = 10, decimal_places = 5, default=0.00)
	cert_code= models.CharField(max_length = 100, null=True)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)


class ExternalCourseMap(models.Model):
	"""mapping of spoken foss id & external course ids"""
	foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT)
	external_course = models.IntegerField() # HN category id
	tag = models.CharField(max_length=120) # Tag for external projects
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

