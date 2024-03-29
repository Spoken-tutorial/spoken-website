# Standard Library
from builtins import str
from builtins import object
import os
from datetime import datetime
import jsonfield

# Third Party Stuff
from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Spoken Tutorial Stuff
from events.models import City, District, Location, State

def profile_picture(instance, filename):
    ext = os.path.splitext(filename)[1]
    ext = ext.lower()
    return '/'.join(['user', str(instance.user.id), str(instance.user.id) + ext])

def profile_picture_thumb(instance, filename):
    ext = os.path.splitext(filename)[1]
    ext = ext.lower()
    return '/'.join(['user', str(instance.user.id), str(instance.user.id) + "-thumb" + ext])

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    confirmation_code = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True, null=True)
    location = models.ForeignKey(Location, null=True, on_delete=models.PROTECT )
    district = models.ForeignKey(District, null=True, on_delete=models.PROTECT )
    city = models.ForeignKey(City, null=True, on_delete=models.PROTECT )
    state = models.ForeignKey(State, null=True, on_delete=models.PROTECT )
    country = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.PositiveIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20, null=True)
    picture = models.FileField(upload_to=profile_picture, null=True, blank=True)
    thumb = models.FileField(upload_to=profile_picture_thumb, null=True, blank=True)
    address = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta(object):
        app_label = 'cms'

class Page(models.Model):
    title = models.CharField(max_length=255)
    css = models.TextField(default=None, null=True, blank=True)
    body = models.TextField()
    js = models.TextField(default=None, null=True, blank=True)
    cols = models.IntegerField(default=9)
    permalink = models.CharField(max_length=255, unique=True)
    formatting = models.BooleanField(default = True)
    target_new = models.BooleanField()
    visible = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

@python_2_unicode_compatible
class Block_Location(models.Model):
    name = models.CharField(max_length=255)
    visible = models.BooleanField()

    def __str__(self):
        return self.name

class Block(models.Model):
    block_location = models.ForeignKey(Block_Location, on_delete=models.PROTECT )
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
    nav = models.ForeignKey(Nav, on_delete=models.PROTECT )
    subnav_title = models.CharField(max_length=255)
    permalink = models.CharField(max_length=255)
    position = models.IntegerField()
    target_new = models.BooleanField()
    visible = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

class SiteFeedback(models.Model):
    name = models.CharField(max_length = 255)
    email =  models.EmailField()
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    
class Event(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    title = models.CharField(max_length = 255)
    body = models.TextField()
    source_link = models.URLField(max_length=255, null=True, blank=True)
    event_date = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT )
    body = models.TextField()
    bg_color = models.CharField(max_length=15, null=True, blank=True)
    start_date = models.DateField(default=datetime.now)
    expiry_date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now = True)

@python_2_unicode_compatible
class NewsType(models.Model):
    name = models.CharField(max_length = 50)
    slug = models.CharField(max_length = 50)
    
    def __str__(self):
        return self.name
        
def content_file_name(instance, filename):
    ext = os.path.splitext(filename)[1]
    ext = ext.lower()
    return '/'.join(['news', str(instance.id), str(instance.id) + ext])

class News(models.Model):
    news_type = models.ForeignKey(NewsType, on_delete=models.PROTECT )
    title = models.CharField(max_length = 255)
    slug = models.CharField(max_length = 255)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.PROTECT )
    picture = models.FileField(upload_to=content_file_name, null=True, blank=True)
    body = models.TextField()
    url = models.URLField(null=True, blank=True)
    url_title = models.CharField(max_length = 200, null=True, blank=True)
    weight = models.PositiveIntegerField(default=3)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT )
    created = models.DateTimeField()
    updated = models.DateTimeField()
    
#    @models.permalink
#    def get_absolute_url(self):
#        return ('views.view_something', (), {'slug': self.slug})
#    
    class Meta(object):
        verbose_name = "New"

class UserType(models.Model):
    STATUS_CHOICES = ((0,'Inactive'),(1,'Active'))
    user = models.ForeignKey(User, on_delete=models.CASCADE,unique=True)
    subscription = models.DateField(null=True,blank=True)
    ilw = jsonfield.JSONField(null=True)
    status = models.CharField(choices=STATUS_CHOICES,max_length=25,default=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)