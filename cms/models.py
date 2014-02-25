from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
	user = models.ForeignKey(User)
	confirmation_code = models.CharField(max_length=255)
	title = models.CharField(max_length=255, blank=True, null=True)
	first_name = models.CharField(max_length=255, blank=True, null=True)
	last_name = models.CharField(max_length=255, blank=True, null=True)
	street = models.CharField(max_length=255, blank=True, null=True)
	location = models.CharField(max_length=255, blank=True, null=True)
	district = models.CharField(max_length=255, blank=True, null=True)
	city = models.CharField(max_length=255, blank=True, null=True)
	state = models.CharField(max_length=255, blank=True, null=True)
	country = models.CharField(max_length=255, blank=True, null=True)
	pincode = models.PositiveIntegerField(blank=True, null=True)
	phone = models.PositiveIntegerField(blank=True, null=True)
	created = models.DateTimeField(auto_now_add=True)
	class Meta:
		app_label = 'cms'

class Page(models.Model):
	title = models.CharField(max_length=255)
	body = models.TextField()
	permalink = models.CharField(max_length=255, unique=True)
	target_new = models.BooleanField()
	visible = models.BooleanField()
	created = models.DateTimeField(auto_now_add=True)

class Block_Location(models.Model):
	name = models.CharField(max_length=255)
	visible = models.BooleanField()

	def __unicode__(self):
		return self.name

class Block(models.Model):
	block_location = models.ForeignKey(Block_Location)
	title = models.CharField(max_length=255)
	body = models.TextField()
	position = models.IntegerField()
	visible = models.BooleanField()
	created = models.DateTimeField(auto_now_add=True)

class Nav(models.Model):
	nav_title = models.CharField(max_length=255)
	permalink = models.CharField(max_length=255)
	position = models.IntegerField()
	target_new = models.BooleanField()
	visible = models.BooleanField()
	created = models.DateTimeField(auto_now_add=True)

class SubNav(models.Model):
	nav = models.ForeignKey(Nav)
	subnav_title = models.CharField(max_length=255)
	permalink = models.CharField(max_length=255)
	position = models.IntegerField()
	target_new = models.BooleanField()
	visible = models.BooleanField()
	created = models.DateTimeField(auto_now_add=True)

