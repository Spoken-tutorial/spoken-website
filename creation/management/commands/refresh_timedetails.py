# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py refresh_timedetails"

# This will refresh contributor list into contributorrole
from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime,timedelta
from django.utils import timezone
from django.db.models import Q
# Spoken Tutorial Stuff
from creation.models import TutorialResource,\
                            TutorialDetail, FossCategory, TutorialDuration
from creation.views import get_video_info                            
from django.conf import settings

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        tresources = TutorialResource.objects.all()
        for tresource in tresources:
            if tresource.video:
                video_path = settings.MEDIA_ROOT + "videos/" + \
                            str(tresource.tutorial_detail.foss.pk) + "/" + str(tresource.tutorial_detail.pk) + "/" + tresource.video
                try:
                    td = TutorialDuration.objects.get(tresource=tresource)
                    if td.created == tresource.updated:
                        continue
                    else:
                        video_info = get_video_info(video_path)
                        td.duration = video_info['duration']
                        td.save()
                        #print(tresource.tutorial_detail.tutorial + "duration updated" + str(video_info['duration']))
                except TutorialDuration.DoesNotExist as e:
                    try:
                        video_info = get_video_info(video_path)
                        TutorialDuration.objects.create(tresource=tresource, duration=video_info['duration'], created=tresource.updated)
                        #print(tresource.tutorial_detail.tutorial + "duration created" + str(video_info['duration']))
                    except Exception as e:
                        print(e)
        print('Completed')
                    
