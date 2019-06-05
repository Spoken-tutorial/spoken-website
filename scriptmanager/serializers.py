from creation.models import ContributorRole, FossCategory, Language,TutorialDetail
from rest_framework import serializers
from .models import Scripts, ScriptDetails

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
    class Meta:
      model = ContributorRole
      fields = ('foss_category','language','user', 'status')


class TutorialDetailSerializer(serializers.ModelSerializer):
    class Meta:
      model=TutorialDetail
      fields=('id','foss','tutorial','level','order','user','created','updated')


class ScriptsGetSerializer(serializers.ModelSerializer):
  tutorial=TutorialDetailSerializer(read_only=True)

  class Meta: 
    model=Scripts
    fields=('id','tutorial','language','status','data_file')


class ScriptsPostSerializer(serializers.ModelSerializer):

  class Meta: 
    model=Scripts
    fields=('id','tutorial','language','status','data_file')
