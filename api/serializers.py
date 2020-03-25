from builtins import object
from django.contrib.auth.models import User
from creation.models import TutorialResource, TutorialDetail, FossSuperCategory, FossCategory, Language
from rest_framework import serializers


class TutorialDetailSerializer(serializers.ModelSerializer):
    tutorial_detail = serializers.CharField(read_only=True)

    class Meta(object):
        model = TutorialDetail


class VideoSerializer(serializers.ModelSerializer):
    tutorial_level = serializers.CharField(source='tutorial_detail.level', read_only=True)
    tutorial_order = serializers.CharField(source='tutorial_detail.order', read_only=True)
    tutorial_name = serializers.CharField(source='tutorial_detail.tutorial', read_only=True)
    
    class Meta(object):
        model = TutorialResource
        fields = ('id','tutorial_name','video_id','tutorial_level','tutorial_order')


class CategorySerializer(serializers.ModelSerializer):
    class Meta(object):
        model = FossSuperCategory
        fields = ('id', 'name')


class FossSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = FossCategory
        fields = ('id', 'foss', 'description')


class LanguageSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = Language
        fields = ('id', 'name')

# class FossSerializer(serializers.Serializer):
# 	course_id = serializers.IntegerField(read_only=True)
# 	description = serializers.CharField(read_only=True)
# 	duration = serializers.CharField(read_only=True)