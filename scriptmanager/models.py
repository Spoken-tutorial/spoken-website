from django.db import models
from creation.models import TutorialDetail, Language
from django.contrib.auth.models import User
# Create your models here.

class Scripts(models.Model):
	tutorial = models.ForeignKey(TutorialDetail)
	language = models.ForeignKey(Language)
	status = models.BooleanField(default=False)
	data_file = models.FileField(upload_to='scripts')
	user = models.ForeignKey(User,related_name='user_id')
	

class ScriptDetails(models.Model):
	cue = models.TextField()
	narration = models.TextField()
	order = models.PositiveIntegerField()
	script = models.ForeignKey(Scripts, on_delete = models.CASCADE)
	comment_status = models.BooleanField(default=False)

class Comments(models.Model):
	comment = models.TextField()
	user=models.ForeignKey(User)
	script_details=models.ForeignKey(ScriptDetails, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
