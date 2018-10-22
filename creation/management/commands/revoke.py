# Code to add publish date in tutorialresource table
# To run this file please follow below instructions:
# 1. Go to project directory
# 2. run "python manage.py revoke"

from __future__ import absolute_import, print_function, unicode_literals

# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime,timedelta
from django.utils import timezone
from django.db.models import Q
# Spoken Tutorial Stuff
from creation.models import TutorialResource, ContributorRole,TutorialsAvailable
from creation.views import send_mail_to_contributor
class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        assignment_status = {
        'un-assigned' : 0
        'assigned' : 1,
        }

        script_status ={
        'not-started' : 0,
        'written' : 1,
        'domain-approved' : 2,
        'quality-approved' : 3,
        'uploaded' : 4
        }

        status ={
        'inactive' : 0,
        'active' : 1
        }
        all_alloted_tuts = TutorialResource.objects.filter(
            assignment_status=assignment_status['assigned'],
            script_status__lt=script_status['uploaded'])

        for a_tutorial in all_alloted_tuts:
            today = datetime.date(timezone.now())
            stale_date = datetime.date(a_tutorial.submissiondate + timezone.timedelta(days = 30))
            if today > stale_date:
                uid = a_tutorial.script_user_id
                lid = a_tutorial.language_id
                tdid = a_tutorial.tutorial_detail_id
                
                tutorialresourceobj = TutorialResource.objects.get(Q(script_user_id=uid)||Q(video_user_id=uid), \
                    tutorial_detail_id = tdid, language_id = lid)
                if tutorialsavailableobj.exists():
                    tutorialsavailableobj.update(assignment_status=assignment_status['un-assigned'])
                
                tutorialsavailableobj = TutorialsAvailable.objects.filter(id = taid)
                if tutorialsavailableobj.exists():
                    tutorialsavailableobj.update(language_id= lid, \
                        tutorial_detail_id= tdid )
                    
                
                contributorrole_active = ContributorRole.objects.filter(user_id=uid, tutorial_detail_id=tdid, language_id=lid, status['active'])
                if contributorrole_active.exists():    
                    #contributorrole_active.update(status=status['inactive'])
                    contributorrole_active.revoke()
                    
                
                #Send email to contributor if he is nearing deadline
                send_mail_to_contributor(uid,tdid,lid,True)
            print ("Exited")
