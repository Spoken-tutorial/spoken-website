from django.db import models
from creation.models import TutorialDetail, Language
from django.contrib.auth.models import User
# Create your models here.

class Scripts(models.Model):
	tutorial = models.OneToOneField(TutorialDetail)
	language = models.ForeignKey(Language,blank=True,null = True)
	status = models.BooleanField(default=False,blank=True)
	data_file = models.FileField(upload_to='scripts',blank=True)
	user = models.ForeignKey(User,related_name='user_id')
	

class ScriptDetails(models.Model):
	cue=models.TextField()
	narration=models.TextField()
	order=models.PositiveIntegerField()
	script=models.ForeignKey('Scripts', on_delete = models.CASCADE)
