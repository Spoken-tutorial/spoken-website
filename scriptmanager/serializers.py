from creation.models import ContributorRole, FossCategory, Language,TutorialDetail
from rest_framework import serializers
from .models import Scripts, ScriptDetails,Comments
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status

class FossCategorySerializer(serializers.ModelSerializer):
  name = serializers.CharField(source='foss')
  class Meta:
    model=FossCategory
    fields=('id','name')

class LanguageSerializer(serializers.ModelSerializer):
  class Meta:
    model=Language
    fields=('id','name')

class ContributorRoleSerializer(serializers.ModelSerializer):
    foss_category=FossCategorySerializer(read_only=True)
    language=LanguageSerializer(read_only=True)
    user=serializers.CharField()
    class Meta:
      model = ContributorRole
      fields = ('foss_category','language','user', 'status')


class TutorialDetailSerializer(serializers.ModelSerializer):
    script_status = serializers.SerializerMethodField()
    class Meta:
      model=TutorialDetail
      fields=('id','foss','tutorial','level','order','script_status')
    
    def get_script_status(self,instance):
      data=Scripts.objects.filter(tutorial_id=instance.id,user=self.context.get('request').user)
      if data:
        return True 
      else:
        return False



class ScriptsDetailSerializer(serializers.ModelSerializer):

  class Meta:
    model=ScriptDetails
    fields=('id','cue','narration','order','script')

class ScriptsSerializer(serializers.ModelSerializer):
  details=ScriptsDetailSerializer(many=True)

  class Meta:
    model=Scripts
    fields=('details',)

class CommentsSerializer(serializers.ModelSerializer):
  user=serializers.CharField()

  class Meta:
    model=Comments
    fields=('id','comment','user','script_details','created','updated')
 