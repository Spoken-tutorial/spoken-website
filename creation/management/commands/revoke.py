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

# Spoken Tutorial Stuff
from creation.models import TutorialResource, ContributorRole,TutorialsAvailable
from creation.views import send_mail_to_contributor
class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        print ("Entered")
        all_alloted_tuts = TutorialResource.objects.filter(assignment_status=1,script_status__lt=4)
        for a_tutorial in all_alloted_tuts:
            today = datetime.date(timezone.now())
            stale_date = datetime.date(a_tutorial.submissiondate + timezone.timedelta(days = 30))
            if today > stale_date:
                print("data : ",datetime.date(a_tutorial.submissiondate),today)
                uid = a_tutorial.script_user_id
                lid = a_tutorial.language_id
                tdid = a_tutorial.tutorial_detail_id
                print( uid,'\n',lid,'\n',tdid)
                try:
                    revoke_this = ContributorRole.objects.get(user_id=uid, language_id=lid, tutorial_detail_id = tdid)
                    revoke_this.status =0 
                    revoke_this.save()

                except:
                    ok =2
                try:
                    tutorialresourceobj = TutorialResource.objects.get(script_user_id=uid ,tutorial_detail_id = tdid, language_id = lid)
                    tutorialresourceobj.assignment_status = 0 
                    tutorialresourceobj.save()

                except :
                    tutorialresourceobj = TutorialResource.objects.get(video_user_id=uid ,tutorial_detail_id = tdid, language_id = lid)
                    tutorialresourceobj.assignment_status = 0 
                    tutorialresourceobj.save()

                try:
                    tutorialsavailableobj = TutorialsAvailable(id = taid)
                    tutorialsavailableobj.language_id = lid
                    tutorialsavailableobj.tutorial_detail_id = tdid
                    tutorialsavailableobj.save()
                
                except :
                    
                    tutorialsavailableobj = TutorialsAvailable()
                    tutorialsavailableobj.language_id = lid
                    tutorialsavailableobj.tutorial_detail_id = tdid
                    tutorialsavailableobj.save()
                    
                try:
                    contributorrole = ContributorRole.objects.get(user_id=uid,tutorial_detail_id=tdid,language_id=lid)
                    contributorrole.status = 0
                    contributorrole.save()
                except :
                    contributorrole = ContributorRole.objects.filter(user_id=uid,tutorial_detail_id=tdid,language_id=lid).update(status=0)
                    
                
                #Send email to contributor if he is nearing deadline
                send_mail_to_contributor(uid,tdid,lid,True)
            print ("Exited")
