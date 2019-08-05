# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py refresh"

# This will refresh contributor list into contributorrole
from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime,timedelta
from django.utils import timezone
from django.db.models import Q
# Spoken Tutorial Stuff
from creation.models import TutorialResource, Language, TutorialsAvailable, TutorialDetail
from creation.views import send_mail_to_contributor
class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        count = 0
        PUBLISHED = 1
        tutorials = TutorialDetail.objects.filter(
            id__in = TutorialResource.objects.filter(status = PUBLISHED,
            language = 22).values('tutorial_detail').distinct())

        lang_qs = Language.objects.all()
        for tutorial in tutorials:
            for a_lang in lang_qs:
                this_lang_tutorial = TutorialResource.objects.filter(Q(
                    status = PUBLISHED)|Q(
                    assignment_status = 1),
                    tutorial_detail = tutorial, language = a_lang
                    )
                if not this_lang_tutorial.exists():
                    tutorialsavailable = TutorialsAvailable.objects.filter(
                        tutorial_detail = tutorial, language = a_lang)
                    if not tutorialsavailable.exists():
                        tutorialsavailable = TutorialsAvailable()
                        tutorialsavailable.tutorial_detail = tutorial
                        tutorialsavailable.language = a_lang
                        tutorialsavailable.save()
                        print(tutorial.tutorial," : ",a_lang," added")
                        count+=1        

