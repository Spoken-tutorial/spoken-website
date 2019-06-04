from creation.models import ContributorRole, FossCategory, Language,TutorialDetail
from rest_framework import serializers
from .models import Scripts

class FossCategoryField(serializers.RelatedField):
  def to_representation(self, value):
    return value.foss

class LanguageField(serializers.RelatedField):
  def to_representation(self, value):
    return value.name
    
class ContributorRoleSerializer(serializers.ModelSerializer):
  foss_category = FossCategoryField(read_only=True)
  language = LanguageField(read_only=True)

  class Meta:
    model = ContributorRole
    fields = ('foss_category', 'language', 'user', 'status')


class TutorialDetailSerializer(serializers.ModelSerializer):
    class Meta:
      model=TutorialDetail
      fields=('id','foss','tutorial','level','order','user','created','updated')

class ScriptsSerializer(serializers.ModelSerializer):
  class Meta:
    model=Scripts
    fields=('id','tutorial','language','status','data_file')
