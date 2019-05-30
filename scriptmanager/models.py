from django.db import models
from creation.models import TutorialDetail, Language
# Create your models here.

class Scripts(models.Model):
	tutorial = models.OneToOneField(TutorialDetail)
	language = models.ForeignKey(Language)
	status = models.BooleanField(default=False)
	data_file = models.FileField(upload_to='scripts')

class ScriptDetails(models.Model):
	cue=models.TextField()
	narration=models.TextField()
	order=models.PositiveIntegerField()
	script=models.ForeignKey(Scripts)
