# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class FossCategories(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    workshop = models.IntegerField()
    foss_desc = models.TextField()
    class Meta:
        managed = False
        db_table = 'foss_categories'

class Role(models.Model):
    rid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=64)
    class Meta:
        managed = False
        db_table = 'role'

class TutorialCommonContents(models.Model):
    id = models.IntegerField(primary_key=True)
    tutorial_detail_id = models.IntegerField()
    tutorial_slide = models.TextField()
    tutorial_slide_uid = models.IntegerField()
    tutorial_slide_status = models.IntegerField()
    tutorial_code = models.TextField()
    tutorial_code_uid = models.IntegerField()
    tutorial_code_status = models.IntegerField()
    tutorial_assignment = models.TextField()
    tutorial_assignment_uid = models.IntegerField()
    tutorial_assignment_status = models.IntegerField()
    tutorial_prerequisit = models.IntegerField()
    tutorial_prerequisit_uid = models.IntegerField()
    tutorial_prerequisit_status = models.IntegerField()
    tutorial_keywords = models.TextField()
    tutorial_keywords_uid = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'tutorial_common_contents'

class TutorialDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    foss_category = models.CharField(max_length=255)
    tutorial_name = models.CharField(max_length=600)
    tutorial_level = models.CharField(max_length=400)
    order_code = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'tutorial_details'

class TutorialDomainReviewerRoles(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.IntegerField()
    language_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'tutorial_domain_reviewer_roles'

class TutorialLanguages(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'tutorial_languages'

class TutorialMissingComponent(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.IntegerField()
    trid = models.IntegerField()
    component = models.CharField(max_length=15)
    type = models.IntegerField()
    remarks = models.TextField()
    reported = models.IntegerField()
    reply_status = models.IntegerField()
    created = models.DateField()
    updated = models.DateField()
    email = models.CharField(max_length=100)
    class Meta:
        managed = False
        db_table = 'tutorial_missing_component'

class TutorialMissingComponentReply(models.Model):
    id = models.IntegerField(primary_key=True)
    missing_component_id = models.IntegerField()
    uid = models.IntegerField()
    reply_message = models.TextField()
    created = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'tutorial_missing_component_reply'

class TutorialPublicReview(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.IntegerField()
    trid = models.IntegerField()
    date_time = models.DateTimeField()
    component = models.CharField(max_length=20)
    comment = models.TextField()
    class Meta:
        managed = False
        db_table = 'tutorial_public_review'

class TutorialPublicReviewVideo(models.Model):
    id = models.IntegerField(primary_key=True)
    tutorial_public_review_id = models.IntegerField()
    item = models.IntegerField()
    everywhere = models.IntegerField()
    video_time = models.TimeField()
    class Meta:
        managed = False
        db_table = 'tutorial_public_review_video'

class TutorialQualityRoles(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.IntegerField()
    language_id = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'tutorial_quality_roles'

class TutorialResources(models.Model):
    id = models.IntegerField(primary_key=True)
    tutorial_detail_id = models.IntegerField()
    uid = models.IntegerField()
    language = models.CharField(max_length=50)
    upload_time = models.DateTimeField()
    reviewer = models.CharField(max_length=400)
    tutorial_content_id = models.IntegerField()
    tutorial_outline = models.TextField()
    tutorial_outline_uid = models.IntegerField()
    tutorial_outline_status = models.IntegerField()
    tutorial_script = models.TextField()
    tutorial_script_uid = models.IntegerField()
    tutorial_script_status = models.IntegerField()
    tutorial_script_timed = models.TextField()
    tutorial_video = models.TextField()
    tutorial_video_uid = models.IntegerField()
    tutorial_video_status = models.IntegerField()
    tutorial_status = models.CharField(max_length=50)
    cvideo_version = models.IntegerField()
    hit_count = models.BigIntegerField()
    request_exception = models.TextField()
    class Meta:
        managed = False
        db_table = 'tutorial_resources'

class TutorialUpdateLog(models.Model):
    id = models.IntegerField(primary_key=True)
    tutorial_resources_id = models.IntegerField()
    update_time = models.DateTimeField()
    updated_by = models.CharField(max_length=255)
    updated_content = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'tutorial_update_log'

class UserRatings(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.IntegerField()
    page_id = models.IntegerField()
    rated_date = models.DateField()
    rating = models.BigIntegerField()
    class Meta:
        managed = False
        db_table = 'user_ratings'

class Users(models.Model):
    uid = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=60)
    pass_field = models.CharField(db_column='pass', max_length=32) # Field renamed because it was a Python reserved word.
    mail = models.CharField(max_length=64, blank=True)
    mode = models.IntegerField()
    sort = models.IntegerField(blank=True, null=True)
    threshold = models.IntegerField(blank=True, null=True)
    theme = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    signature_format = models.IntegerField()
    created = models.IntegerField()
    access = models.IntegerField()
    login = models.IntegerField()
    status = models.IntegerField()
    timezone = models.CharField(max_length=8, blank=True)
    language = models.CharField(max_length=12)
    picture = models.CharField(max_length=255)
    init = models.CharField(max_length=64, blank=True)
    data = models.TextField(blank=True)
    last_login = models.DateTimeField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'users'

class UsersRoles(models.Model):
    uid = models.IntegerField()
    rid = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'users_roles'

class VideoComments(models.Model):
    id = models.IntegerField(primary_key=True)
    tutorial_resource_id = models.IntegerField()
    uid = models.IntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'video_comments'

