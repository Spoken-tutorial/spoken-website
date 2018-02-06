from django.contrib.auth.models import User
from creation.models import TutorialResource
from rest_framework import serializers

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorialResource
        fields = ('id','language','video_id')

