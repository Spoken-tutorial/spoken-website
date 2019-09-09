# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py super_admin_refresh_roles"

from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime,timedelta
from django.utils import timezone
from django.db.models import Q, Count
# Spoken Tutorial Stuff
from creation.models import TutorialResource, ContributorRole,TutorialsAvailable, TutorialDetail, RoleRequest
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

        STATUS_DICT ={
        'inactive' : 0,
        'active' : 1
        }

        UNPUBLISHED = 0
        PUBLISHED = 1
        SUPER_ADMIN_USER_ID = 7
        try:
            super_admin_contributor_languages = RoleRequest.objects.filter(role_type = 0,
                user_id=SUPER_ADMIN_USER_ID, status = STATUS_DICT['active'], language_id__isnull= False).values(
                'language').distinct()
            tutorial_resource = TutorialResource.objects.filter(
                language_id__in = super_admin_contributor_languages)
            count = 0            
            for tutorial in tutorial_resource:
                super_admin_contrib_roles = ContributorRole.objects.filter(
                    user_id = SUPER_ADMIN_USER_ID, language_id = tutorial.language,
                    tutorial_detail_id = tutorial.tutorial_detail)
                if not super_admin_contrib_roles.exists():
                    count +=1
                
                    add_previous_contributor_role = ContributorRole()
                    add_previous_contributor_role.foss_category_id = tutorial.tutorial_detail.foss_id
                    add_previous_contributor_role.language_id = tutorial.language_id
                    add_previous_contributor_role.user_id = SUPER_ADMIN_USER_ID
                    add_previous_contributor_role.status = STATUS_DICT['active']
                    add_previous_contributor_role.tutorial_detail_id = tutorial.tutorial_detail_id
                    add_previous_contributor_role.save()
                    
                    print (tutorial.tutorial_detail.foss_id, tutorial.language.name,
                            tutorial.tutorial_detail.tutorial)        
            print("Count :",count)
            print ("Exited")
        
        except Exception as e:
            raise e
        