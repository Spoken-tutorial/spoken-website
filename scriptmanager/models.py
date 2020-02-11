from django.db import models
from creation.models import TutorialDetail, Language
from django.contrib.auth.models import User
# Create your models here.

class Script(models.Model):
	tutorial = models.ForeignKey(TutorialDetail)
	language = models.ForeignKey(Language)
	suggested_title = models.CharField(max_length=255, null=True)
	status = models.BooleanField(default=False)
	data_file = models.FileField(upload_to='scripts')
	user = models.ForeignKey(User,related_name='user_id', null=True)
	ordering = models.TextField(default='')
	published_by = models.ForeignKey(User, null=True)
	published_on = models.DateTimeField(null=True)

	def __str__(self):
		return str(self.tutorial) + ' - ' + str(self.language)

class ScriptDetail(models.Model):
	cue = models.TextField(blank=True)
	narration = models.TextField(blank=True)
	order = models.PositiveIntegerField()
	script = models.ForeignKey(Script, on_delete = models.CASCADE)
	comment_status = models.BooleanField(default=False)

class Comment(models.Model):
	comment = models.TextField()
	user=models.ForeignKey(User)
	script_details=models.ForeignKey(ScriptDetail, on_delete=models.CASCADE)
	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	done = models.BooleanField(default=False)
	resolved = models.BooleanField(default=False)

	def __str__(self):
	 return str(self.user) + ' - ' + self.comment
