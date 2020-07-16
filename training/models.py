from django.db import models
from builtins import str
from builtins import object

#import auth user models
from django.contrib.auth.models import User
from creation.models import FossCategory, Language
from events.models import *


class TrainingEvents(models.Model):
	EVENT_TYPE_CHOICES =(
	('', '-----'), ('FDP', 'FDP'), ('SDP', 'SDP'), ('Workshop', 'Workshop'),
	)

	event_type = models.CharField(max_length = 50, choices = EVENT_TYPE_CHOICES)
	event_name = models.CharField(max_length=200)
	state = models.ForeignKey(State, on_delete=models.PROTECT )
	host_college = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT )
	foss = models.ForeignKey(FossCategory, on_delete=models.PROTECT )
	Language_of_workshop = models.ForeignKey(Language, on_delete=models.PROTECT )
	event_start_date = models.DateField(default=datetime.now)
	event_end_date = models.DateField(default=datetime.now)
	event_coordinator_name =  models.CharField(max_length=200)
	event_coordinator_email = models.EmailField(null=True)
	event_coordinator_contact_no = models.CharField(max_length = 100, null=True)
	registartion_start_date = models.DateField(default=datetime.now)
	registartion_end_date = models.DateField(default=datetime.now)
	entry_date = models.DateTimeField(auto_now_add = True)
	entry_user = models.ForeignKey(User, on_delete=models.PROTECT)


	def __str__(self):
		return self.event_name


class EventRegistartion(models.Model):
	event = models.ForeignKey(TrainingEvents, on_delete=models.PROTECT)
	participant_name =  models.CharField(max_length=200)
	participant_email = models.EmailField()
	gender = models.CharField(max_length=200)
	state = models.ForeignKey(State, on_delete=models.PROTECT )
	college = models.ForeignKey(AcademicCenter, on_delete=models.PROTECT)
	department = models.ForeignKey(Department, on_delete=models.PROTECT )
	created = models.DateTimeField(auto_now_add = True)
