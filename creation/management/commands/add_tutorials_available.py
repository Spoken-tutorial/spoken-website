# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py add_tutorials_available"

from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx

# Spoken Tutorial Stuff
from creation.models import TutorialResource, TutorialsAvailable, Language

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        count = 0
        tutorials = TutorialResource.objects.filter(script_status =4,language = 22)
            
        for tutorial in tutorials:
            sam = Language.objects.exclude(id__in = TutorialResource.objects.filter(assignment_status__gte = 1,tutorial_detail = tutorial.tutorial_detail).values('language'))
            for a_lang in sam:
                    already_present = TutorialsAvailable.objects.filter(tutorial_detail=tutorial.tutorial_detail.id,language=a_lang ).exists()
                    if already_present:
                        print("already_present : ",already_present)
                    else:
                        print("Adding to TutorialsAvailable : ",tutorial.tutorial_detail.id," : ",a_lang )
                        tutorialsavailable =  TutorialsAvailable()
                        tutorialsavailable.tutorial_detail = tutorial.tutorial_detail
                        tutorialsavailable.language =  a_lang
                        count +=1
                        tutorialsavailable.save()
                        

        print('---- Script Completed. TutorialsAvailable table updated date added --- ',count)
