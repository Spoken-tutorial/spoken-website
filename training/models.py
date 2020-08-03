from django.db import models
from builtins import str
from builtins import object

#import auth user models
from django.contrib.auth.models import User
from creation.models import FossCategory, Language
from events.models import *
from .helpers import EVENT_TYPE_CHOICES, REGISTRATION_TYPE_CHOICES
from donate.models import Payee
from donate.helpers import GENDER_CHOICES
import json

class TrainingEvents(models.Model):	

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
	training_status = models.PositiveSmallIntegerField(default=0)
	entry_date = models.DateTimeField(auto_now_add = True)
	entry_user = models.ForeignKey(User, on_delete=models.PROTECT)


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
	payment_status = models.ForeignKey(Payee, on_delete=models.PROTECT, null=True)

	def get_foss_langs(self):
		selected_foss = {}
		cd_foss_langs = TrainingEvents.objects.get(id=self.event.id)
		foss_json = json.dumps(cd_foss_langs.foss.id)
		def_langs_json = json.dumps(cd_foss_langs.Language_of_workshop.id)
		if self.foss_language :
			user_langs_json = json.dumps(self.foss_language.id)
			selected_foss[foss_json] = [[def_langs_json,user_langs_json],0]
		else:
			selected_foss[foss_json] = [[def_langs_json],0]
		return json.dumps(selected_foss)

