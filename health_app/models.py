# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Category(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=255)
    date_added = models.DateTimeField()
    description = models.CharField(max_length=2000)
    image_path = models.CharField(max_length=255)
    status = models.TextField()  # This field type is a guess.
    user_id = models.BigIntegerField(blank=True, null=True)
    order_value = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'category'


class TopicCategory(models.Model):
    topic_category_id = models.IntegerField(primary_key=True)
    order_value = models.IntegerField(blank=True, null=True)
    status = models.TextField()  # This field type is a guess.
    category_id = models.IntegerField(blank=True, null=True)
    topic_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'topic_category'


class HNLanguage(models.Model):
    lan_id = models.IntegerField(primary_key=True)
    date_added = models.DateTimeField()
    lang_name = models.CharField(max_length=255)
    status = models.TextField()  # This field type is a guess.
    user_id = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'language'

    def __str__(self):
        return self.lang_name


class HNContributorRole(models.Model):
    id = models.IntegerField(primary_key=True)
    date_added = models.DateTimeField(blank=True, null=True)
    language_id = models.IntegerField(blank=True, null=True)
    topic_cat_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contributor_role'
