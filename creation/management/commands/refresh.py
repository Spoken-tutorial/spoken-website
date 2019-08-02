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
from creation.models import TutorialResource, ContributorRole,TutorialsAvailable, TutorialDetail
from creation.views import send_mail_to_contributor
class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        ASSIGNMENT_STATUS = {
        'un-assigned' : 0,
        'assigned' : 1,
        }

        SCRIPT_STATUS ={
        'not-started' : 0,
        'written' : 1,
        'domain-approved' : 2,
        'quality-approved' : 3,
        'uploaded' : 4
        }

        STATUS ={
        'inactive' : 0,
        'active' : 1
        }

        UNPUBLISHED = 0
        PUBLISHED = 1

        contributorrole_tutorial_isnull = ContributorRole.objects.filter(status= STATUS['active'],
            tutorial_detail_id__isnull = True).order_by('user_id','language_id')
        for contributor_role in contributorrole_tutorial_isnull:
            
            foss_tutorials = TutorialDetail.objects.filter(foss_id = contributor_role.foss_category_id).order_by('foss_id')
            for tutorial in foss_tutorials:
                tutorial_resource = TutorialResource.objects.filter(Q(
                    outline_user_id=contributor_role.user_id)|Q(
                    script_user_id=contributor_role.user_id)|Q(
                    video_user_id=contributor_role.user_id)|Q(
                    tutorial_detail_id = tutorial,
                    language_id = contributor_role.language_id))
                if tutorial_resource.exists():
                    add_previous_contributor_role = ContributorRole()
                    add_previous_contributor_role.foss_category_id = contributor_role.foss_category_id
                    add_previous_contributor_role.language_id = contributor_role.language_id
                    add_previous_contributor_role.user_id = contributor_role.user_id
                    add_previous_contributor_role.status = 1
                    add_previous_contributor_role.tutorial_detail_id = tutorial.id
                    add_previous_contributor_role.save()
                    tutorial_resource.update(assignment_status = ASSIGNMENT_STATUS['assigned'])
                    
                    print (contributor_role.foss_category_id, contributor_role.language.name,
                            contributor_role.user_id, tutorial.tutorial)        
            delete_contributor_role = ContributorRole.objects.get(
                        id=contributor_role.id).delete()

        print ("Exited")