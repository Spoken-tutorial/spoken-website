# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py add_publish_date"

from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx

# Spoken Tutorial Stuff
from creation.models import TutorialResource

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        # Get data from database
        try:
            existing_video_list = TutorialResource.objects.filter(video__gt="").values_list("pk", "video", "language_id__name")
            for row in existing_video_list:
                audio_name  = row[1].rsplit('.')[0]
                # To ensure database is not corrupted on running this script again by mistake.
                if audio_name.rsplit('-',1)[1] != "Video":
                    TutorialResource.objects.filter(pk=row[0]).update(audio=audio_name+".ogg", video=audio_name.rsplit(row[2])[0]+"Video.webm")
        except Exception as error:
            print ("1001:", error)