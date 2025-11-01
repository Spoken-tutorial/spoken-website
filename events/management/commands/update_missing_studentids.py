
# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime,timedelta
from django.utils import timezone
from django.db.models import Q
from builtins import str
from django.contrib.auth.models import User
from mdldjango.models import MdlUser
from events.models import *

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        print('>> adding stuentid to testattendance')
        count =0
        no_count=0
        _file = open('missingstudent.log', 'w')
        t_attendnces = TestAttendance.objects.filter(student_id__isnull=True)
        for tea in t_attendnces:
            try:
                mdluser=MdlUser.objects.get(id=tea.mdluser_id)
                if not mdluser:
                    _file.write(str(tea.id)+',mdluser not present\n')
                student=Student.objects.get(user__email=mdluser.email)
                if not student:
                    _file.write(str(tea.id)+',student not present\n')
                tea.student_id=student.id
                tea.save()
                count = count + 1
            except:
                _file.write(str(tea.id)+',not updated\n')
                no_count=no_count+1

        _file.write('>> Script Completed. students added, '+str(count)+'\n')
        _file.write('>> Script Completed. students not added, '+str(no_count)+'\n')
        _file.close()    
        print(('>> Script Completed. students added',count))
        print(('>> Script Completed. students not added',no_count))
