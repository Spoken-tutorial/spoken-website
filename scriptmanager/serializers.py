from creation.models import ContributorRole, FossCategory, Language, TutorialDetail,TutorialResource
from rest_framework import serializers
from .models import Script, ScriptDetail, Comment
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta


class FossCategorySerializer(serializers.ModelSerializer):
  name = serializers.CharField(source='foss')

  class Meta:
    model = FossCategory
    fields = ('id', 'name','description')


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
    outline=serializers.SerializerMethodField()
    language=serializers.SerializerMethodField()

    class Meta:
      model = TutorialDetail
      fields = ('id', 'foss','language', 'tutorial', 'level', 'order', 'script_status','outline')

    def get_script_status(self, instance):
      if Script.objects.filter(tutorial_id=instance.id,language = self.context.get('lang'),user=self.context.get('user')).exists():
        return True
      else:
        return False
      
    def get_outline(self,instance):
        lang=Language.objects.filter(id=self.context.get('lang'))
        if TutorialResource.objects.filter(tutorial_detail=instance,language=lang).exists():
          return TutorialResource.objects.filter(tutorial_detail=instance,language=lang)[0].outline
        else:
          return None

    def get_language(self,instance):
        lang_id=self.context.get('lang')
        return int(lang_id)


class ScriptDetailSerializer(serializers.ModelSerializer):

  class Meta:
    model = ScriptDetail
    fields = ('id', 'cue', 'narration', 'order', 'comment_status', 'script')

class ScriptSerializer(serializers.ModelSerializer):
  details = ScriptDetailSerializer(many=True)

  class Meta:
    model = Script
    fields = ('details',)


class CommentSerializer(serializers.ModelSerializer):
  user = serializers.CharField()
  time = serializers.SerializerMethodField()

  class Meta:
    model = Comment
    fields = ('id', 'comment', 'user', 'script_details', 'time')

  def get_time(self, instance):
    time = datetime.now()
    created=instance.created
    if created.day  == time.day and created.month  == time.month and created.year  == time.year and created.hour == time.hour:
      return str(time.minute - created.minute) + " minute(s) ago"
    elif created.day  == time.day and created.month  == time.month and created.year  == time.year:
      return str(time.hour - created.hour) + " hour(s) ago"
    elif created.month == time.month and created.year  == time.year:
      return str(time.day - created.day) + " day(s) ago" 
    elif created.year == time.year:
          return str(time.month - created.month) + " month(s) ago"
    return date(day=created.day, month=created.month, year=created.year).strftime('%d %B %Y')
  
class ReversionSerializer(serializers.Serializer):
  reversion_id=serializers.IntegerField()
  id = serializers.IntegerField()
  cue = serializers.CharField()
  narration = serializers.CharField()
  order = serializers.CharField()
  script_id = serializers.CharField()
  date_time=serializers.DateTimeField()
  user=serializers.CharField()
