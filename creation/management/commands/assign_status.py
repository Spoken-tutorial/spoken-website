# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py assign_status"

from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime
# Spoken Tutorial Stuff
from creation.models import TutorialResource, PublishTutorialLog,PublicReviewLog

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        count_of_status_0 =0 
        count_of_status_1 =0
        # Assignment status = 2
        tut_null = TutorialResource.objects.filter(status__gte=1,publish_at__isnull=False)
        print("Assignment status - 2 count : ",tut_null.count())
        for tutorials in tut_null:
            tutorials.assignment_status = 2
            tutorials.save()
        tut_null_yes = TutorialResource.objects.filter(status=0,publish_at__isnull=True)
        print("Assignment status -1 count : ",tut_null_yes.count())
        for tutorials in tut_null_yes:
            if tutorials.outline_status > 0 or tutorials.script_status > 0 or tutorials.video_status > 0 :
                count_of_status_1 +=1 ;
                tutorials.assignment_status = 1
                tutorials.save()
            else:
                count_of_status_0 +=1;
                tutorials.assignment_status = 0 
                tutorials.save()
        print('>> Script Completed. Assignment Status updated ',count_of_status_1,count_of_status_0)
