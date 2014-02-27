from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Photo( models.Model ):
    file = models.FileField( upload_to = settings.STATIC_URL + '/creation/uploads/' )

class Language(models.Model):
	name = models.CharField(max_length = 255, unique = True)
	user = models.ForeignKey(User)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

	def __unicode__(self):
		return self.name

class Foss_Category(models.Model):
	foss = models.CharField(unique=True, max_length = 255)
	description = models.TextField()
	status = models.BooleanField(max_length = 2)
	user = models.ForeignKey(User)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

	class Meta:
		verbose_name = 'FOSS Category'

	def __unicode__(self):
		return self.foss

class Level(models.Model):
	level = models.CharField(max_length = 255)

	class Meta:
		verbose_name = 'Tutorial Level'

	def __unicode__(self):
		return self.level

class Tutorial_Detail(models.Model):
	foss = models.ForeignKey(Foss_Category)
	tutorial = models.CharField(max_length = 255)
	level = models.ForeignKey(Level)
	order = models.IntegerField()
	user = models.ForeignKey(User)
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

	class Meta:
		verbose_name = 'Tutorial Detail'
		unique_together = (('foss', 'tutorial', 'level'),)

	def __unicode__(self):
		return self.tutorial

class Contributor_Role(models.Model):
	foss_category = models.ForeignKey(Foss_Category)
	language = models.ForeignKey(Language)
	user = models.ForeignKey(User)
	status = models.BooleanField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

	class Meta:
		unique_together = (('user','foss_category', 'language',),)
		verbose_name = 'Contributor Role'

class Domain_Reviewer_Role(models.Model):
	foss_category = models.ForeignKey(Foss_Category)
	language = models.ForeignKey(Language)
	user = models.ForeignKey(User)
	status = models.BooleanField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

	class Meta:
		unique_together = (('user','foss_category', 'language',),)
		verbose_name = 'Domain Reviewer Role'

class Quality_Reviewer_Role(models.Model):
	foss_category = models.ForeignKey(Foss_Category)
	language = models.ForeignKey(Language)
	user = models.ForeignKey(User)
	status = models.BooleanField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

	class Meta:
		unique_together = (('user','foss_category', 'language',),)
		verbose_name = 'Quality Reviewer Role'

class Tutorial_Common_Content(models.Model):
	tutorial_detail = models.ForeignKey(Tutorial_Detail, unique=True)
	slide = models.CharField(max_length = 255)
	slide_user = models.ForeignKey(User, related_name='slides')
	slide_status = models.PositiveSmallIntegerField()

	code = models.CharField(max_length = 255)
	code_user = models.ForeignKey(User, related_name='codes')
	code_status = models.PositiveSmallIntegerField()

	assignment = models.CharField(max_length = 255)
	assignment_user = models.ForeignKey(User, related_name='assignments')
	assignment_status = models.PositiveSmallIntegerField()

	prerequisit = models.CharField(max_length = 255)
	prerequisit_user = models.ForeignKey(User, related_name='prerequisits')
	prerequisit_status = models.PositiveSmallIntegerField()

	keyword = models.TextField()
	keyword_user = models.ForeignKey(User, related_name='keywords')
	keyword_status = models.PositiveSmallIntegerField()

	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

	class Meta:
		verbose_name = 'Tutorial Common Content'

class Tutorial_Resource(models.Model):
	tutorial_detail = models.ForeignKey(Tutorial_Detail)
	common_content = models.ForeignKey(Tutorial_Common_Content)
	language = models.ForeignKey(Language)

	outline = models.TextField()
	outline_user = models.ForeignKey(User, related_name='outlines')
	outline_status = models.PositiveSmallIntegerField()

	script = models.URLField(max_length = 255)
	script_user = models.ForeignKey(User, related_name='scripts')
	script_status = models.PositiveSmallIntegerField()
	timed_script = models.URLField(max_length = 255)

	video = models.CharField(max_length = 255)
	video_user = models.ForeignKey(User, related_name='videos')
	video_status = models.PositiveSmallIntegerField()

	status = models.PositiveSmallIntegerField()
	version = models.PositiveSmallIntegerField()
	hit_count = models.PositiveIntegerField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

	class Meta:
		unique_together = (('tutorial_detail', 'language',),)

class Archived_Video(models.Model):
	tutorial_resource = models.ForeignKey(Tutorial_Resource)
	user = models.ForeignKey(User)
	version = models.PositiveSmallIntegerField()
	video = models.CharField(max_length = 255)
	atype = models.PositiveSmallIntegerField()
	created = models.DateTimeField(auto_now_add = True)
	updated = models.DateTimeField(auto_now = True)

class Video_Review_Log(models.Model):
	user = models.ForeignKey(User)
	tutorial_resource = models.ForeignKey(Tutorial_Resource)
	component = models.CharField(max_length = 255)
	status = models.PositiveSmallIntegerField()
	created = models.DateTimeField(auto_now_add = True)

class Domain_Review_Log(models.Model):
	user = models.ForeignKey(User)
	tutorial_resource = models.ForeignKey(Tutorial_Resource)
	component = models.CharField(max_length = 255)
	status = models.PositiveSmallIntegerField()
	created = models.DateTimeField(auto_now_add = True)

class Quality_Review_Log(models.Model):
	user = models.ForeignKey(User)
	tutorial_resource = models.ForeignKey(Tutorial_Resource)
	component = models.CharField(max_length = 255)
	status = models.PositiveSmallIntegerField()
	created = models.DateTimeField(auto_now_add = True)

class Contributor_Log(models.Model):
	user = models.ForeignKey(User)
	tutorial_resource = models.ForeignKey(Tutorial_Resource)
	component = models.CharField(max_length = 255)
	status = models.PositiveSmallIntegerField()
	created = models.DateTimeField(auto_now_add = True)
