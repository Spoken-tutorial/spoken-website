# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py refresh_timedetails"

# This will refresh contributor list into contributorrole
from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime, timedelta
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
        count = 0
        check = True
        time = 0
        tutorials = TutorialDetail.objects.all()
        for tutorial in tutorials:
            try:
                tr_rec = TutorialResource.objects.get(
                    tutorial_detail_id=tutorial.id, language_id=22)
                video_path = settings.MEDIA_ROOT + "videos/" + \
                    str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
                video_info = get_video_info(video_path)
                time = video_info['duration']
                check = True
            except Exception as e:
                check = False
                time = 0
                print(e)

            '''This logic is written to handle this error.
                An error occurred in the current transaction.
                You can't execute queries until the end of the 'atomic' block. '''

            if check:
                tutorial_time = TutorialDuration()
                tutorial_time.foss = tutorial.foss_id
                tutorial_time.tutorial = tutorial
                tutorial_time.duration = time
                tutorial_time.save()
