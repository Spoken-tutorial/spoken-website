from creation.models import ContributorRole, FossCategory, Language, TutorialDetail, TutorialResource
from rest_framework import serializers
from .models import Script, ScriptDetail, Comment
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, date, timedelta

class FossCategorySerializer(serializers.ModelSerializer):
  name = serializers.CharField(source='foss')

  class Meta:
    model = FossCategory
    fields = ('id', 'name', 'description')


class LanguageSerializer(serializers.ModelSerializer):

  class Meta:
    model = Language
    fields = ('id', 'name')


class ContributorRoleSerializer(serializers.ModelSerializer):
  foss_category = FossCategorySerializer(read_only=True)
  language = LanguageSerializer(read_only=True)
  user = serializers.CharField()

  class Meta:
    model = ContributorRole
    fields = ('foss_category', 'language', 'user', 'status')


class TutorialDetailSerializer(serializers.ModelSerializer):
  script_status = serializers.SerializerMethodField()
  published = serializers.SerializerMethodField()
  outline = serializers.SerializerMethodField()
  language = serializers.SerializerMethodField()
  published_by = serializers.SerializerMethodField()
  published_on = serializers.SerializerMethodField()
  created_by = serializers.SerializerMethodField()
  foss = FossCategorySerializer(read_only=True)

  class Meta:
    model = TutorialDetail
    fields = ('id', 'foss', 'language', 'tutorial', 'level', 'order', 'script_status', 'outline', 'published', 'published_on', 'published_by', 'created_by')

  def get_script_status(self, instance):
    if Script.objects.filter(tutorial_id=instance.id, language=self.context.get('lang')).exists():
      return True
    else:
      return False
  
  def get_published(self, instance):
    if self.get_script_status(instance):
      return Script.objects.get(tutorial_id=instance.id, language=self.context.get('lang')).status

    return False

  def get_published_on(self, instance):
    if self.get_script_status(instance):
      return Script.objects.get(tutorial_id=instance.id, language=self.context.get('lang')).published_on

    return None

  def get_published_by(self, instance):
    if self.get_script_status(instance):
      user = Script.objects.get(tutorial_id=instance.id, language=self.context.get('lang')).published_by

      if (user):  return user.username

    return None

  def get_created_by(self, instance):
    if self.get_script_status(instance):
      user = Script.objects.get(tutorial_id=instance.id, language=self.context.get('lang')).published_by

      if (user):  return user.username

    return None

  def get_outline(self, instance):
    lang = Language.objects.filter(id=self.context.get('lang'))
    if TutorialResource.objects.filter(tutorial_detail=instance, language=lang).exists():
      return TutorialResource.objects.filter(tutorial_detail=instance, language=lang)[0].outline
    else:
      return None

  def get_language(self, instance):
    lang_id = self.context.get('lang')
    return int(lang_id)

# class TutorialScriptDetailSerializer(serializers.ModelSerializer):
#   outline = serializers.SerializerMethodField()
#   language = serializers.SerializerMethodField()

#   class Meta:
#     model = TutorialDetail
#     fields = ('id', 'foss', 'language', 'tutorial', 'level', 'order', 'outline')

#   def get_outline(self, instance):
#     script = self.context.get('script')
#     lang = script.language
#     if TutorialResource.objects.filter(tutorial_detail=instance, language=lang).exists():
#       return TutorialResource.objects.filter(tutorial_detail=instance, language=lang)[0].outline
#     else:
#       return None

#   def get_language(self, instance):
#     script = self.context.get('script')
#     lang_id = script.language.id
#     return int(lang_id)

class ScriptDetailSerializer(serializers.ModelSerializer):

  class Meta:
    model = ScriptDetail
    fields = ('id', 'cue', 'narration', 'order', 'comment_status', 'script')


class ScriptSerializer(serializers.ModelSerializer):
  slides = serializers.SerializerMethodField()

  # def __init__(self, *args, **kwargs):
  #   remove_fields = kwargs.pop('remove_fields', None)
  #   super(ScriptSerializer, self).__init__(*args, **kwargs)

  #   if remove_fields:
  #       # for multiple fields in a list
  #       for field_name in remove_fields:
  #           self.fields.pop(field_name)

  class Meta:
    model = Script
    fields = ('id', 'slides', 'status', 'tutorial', 'language')

  def get_slides(self, instance):
    slides = ScriptDetail.objects.filter(script=instance)
    ordering = instance.ordering

    if (len(ordering) != 0):
      ordering = ordering.split(',')
      ordering = list(map(int, ordering))
      slides = sorted(slides, key=lambda s: ordering.index(s.pk))

    return ScriptDetailSerializer(slides, many=True).data


class CommentSerializer(serializers.ModelSerializer):
  user = serializers.CharField()
  time = serializers.SerializerMethodField()

  class Meta:
    model = Comment
    fields = ('id', 'comment', 'user', 'script_details', 'time')

  def get_time(self, instance):
    time = datetime.now()
    created = instance.created
    if created.day == time.day and created.month == time.month and created.year == time.year and created.hour == time.hour:
      return str(time.minute - created.minute) + " minute(s) ago"
    elif created.day == time.day and created.month == time.month and created.year == time.year:
      return str(time.hour - created.hour) + " hour(s) ago"
    elif created.month == time.month and created.year == time.year:
      return str(time.day - created.day) + " day(s) ago"
    elif created.year == time.year:
      return str(time.month - created.month) + " month(s) ago"
    return date(day=created.day, month=created.month, year=created.year).strftime('%d %B %Y')


class ReversionSerializer(serializers.Serializer):
  reversion_id = serializers.IntegerField()
  id = serializers.IntegerField()
  cue = serializers.CharField()
  narration = serializers.CharField()
  order = serializers.CharField()
  script_id = serializers.CharField()
  date_time = serializers.DateTimeField()
  user = serializers.CharField()
