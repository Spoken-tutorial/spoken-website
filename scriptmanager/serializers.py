from creation.models import ContributorRole, FossCategory, Language,TutorialDetail
from rest_framework import serializers
from .models import Scripts

class FossCategorySerializer(serializers.ModelSerializer):
  foss_category=serializers.CharField(read_only=True)
  
  class Meta:
    model=FossCategory

class LanguageSerializer(serializers.ModelSerializer):
  language=serializers.CharField(read_only=True)

  class Meta:
    model=Language

class ContributorRoleSerializer(serializers.ModelSerializer):
  foss_id = serializers.CharField(source='foss_category.id', read_only=True)
  foss_category = serializers.CharField(source='foss_category.foss', read_only=True)
  language_id = serializers.CharField(source='language.id', read_only=True)
  language_name = serializers.CharField(source='language.name', read_only=True)
  
  class Meta:
    model = ContributorRole
    fields = ('foss_id','foss_category','language_id','language_name','user', 'status')

class TutorialDetailSerializer(serializers.ModelSerializer):
    class Meta:
      model=TutorialDetail
      fields=('id','foss','tutorial','level','order','user','created','updated')

class ScriptsSerializer(serializers.ModelSerializer):
  class Meta:
    model=Scripts
    fields=('id','tutorial','language','status','data_file')
