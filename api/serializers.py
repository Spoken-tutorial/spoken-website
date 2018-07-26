from django.contrib.auth.models import User
from creation.models import TutorialResource, TutorialDetail
from rest_framework import serializers

class TutorialDetailSerializer(serializers.ModelSerializer):
    tutorial_detail = serializers.CharField(read_only=True)

    class Meta:
        model = TutorialDetail


class VideoSerializer(serializers.ModelSerializer):
    tutorial_level = serializers.CharField(source='tutorial_detail.level', read_only=True)
    tutorial_order = serializers.CharField(source='tutorial_detail.order', read_only=True)
    tutorial_name = serializers.CharField(source='tutorial_detail.tutorial', read_only=True)
    class Meta:
        model = TutorialResource
        fields = ('id','tutorial_name','video_id','tutorial_level','tutorial_order')

