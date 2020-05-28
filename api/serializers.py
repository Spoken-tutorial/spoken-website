from builtins import object
from django.contrib.auth.models import User
from creation.models import TutorialResource, TutorialDetail, FossSuperCategory, FossCategory, Language
from rest_framework import serializers
from django.conf import settings
from creation.views import get_video_info

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



class RelianceJioVideoSerializer(serializers.ModelSerializer):
    """
    video serializer for filtering selected videos.
    """
    description = serializers.ReadOnlyField(source='outline')
    sources = serializers.SerializerMethodField() 
    card = serializers.SerializerMethodField()
    background = serializers.SerializerMethodField()
    title = serializers.ReadOnlyField(source='tutorial_detail.tutorial')
    studio = serializers.ReadOnlyField(source='tutorial_detail.foss.foss')
    duration = serializers.SerializerMethodField()
    production = serializers.ReadOnlyField(source='publish_at')

    class Meta:
        model = TutorialResource
        fields = ('description', 'sources', 'card', 'background', 'title', 'studio', 'duration', 'production')

    def get_sources(self, obj):
        return [self.context['request'].build_absolute_uri(settings.MEDIA_URL+'videos/'+str(obj.tutorial_detail.foss.pk)+'/'+\
                str(obj.tutorial_detail.pk)+'/'+obj.video)]
    def get_card(self, obj):
        return [self.context['request'].build_absolute_uri(settings.MEDIA_URL + 'videos/' +\
                str(obj.tutorial_detail.foss.pk) + '/' + str(obj.tutorial_detail.pk) + '/' +\
                obj.tutorial_detail.tutorial.replace(' ', '-') + '-' + 'Small' + '.png')]
    def get_background(self, obj):
        return [self.context['request'].build_absolute_uri(settings.MEDIA_URL + 'videos/' +\
                str(obj.tutorial_detail.foss.pk) + '/' + str(obj.tutorial_detail.pk) + '/' +\
                obj.tutorial_detail.tutorial.replace(' ', '-') + '-' + 'Big' + '.png')]
    def get_duration(self, obj):
        video_path = settings.MEDIA_ROOT+'videos/'+str(obj.tutorial_detail.foss.pk)+'/'+\
            str(obj.tutorial_detail.pk)+'/'+obj.video
        video_info = get_video_info(video_path)
        return video_info['duration']

class RelianceCategoryJioSerializer(serializers.Serializer):
    category = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()


    def get_videos(self, obj): 
        return self.context.get('videos')

    def get_category(self, obj):
        return 'Health and Nutrition'

class RelianceJioSerializer(serializers.Serializer):
    spokentutorials = serializers.SerializerMethodField()

    def get_spokentutorials(self, obj):
        return [self.context.get('spokentutorials')]
