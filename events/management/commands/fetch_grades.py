#fetch student grades from otc to testattendance table
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime,timedelta
from django.utils import timezone
from django.db.models import Q
from builtins import str
from django.contrib.auth.models import User
from mdldjango.models import MdlUser, MdlQuizGrades
from events.models import *

class Command(BaseCommand):

	@tx.atomic
	def handle(self, *args, **options):
		print('>> adding student grades to testattendance')
		count =0
		no_count=0
		_file = open('getstudentgrades.log', 'w')

		t_attendnces = TestAttendance.objects.filter(status__gte=3)
		
		for tea in t_attendnces:
			try:
				quiz_grade=MdlQuizGrades.objects.get(userid=tea.mdluser_id, quiz=tea.mdlquiz_id)
				if not quiz_grade:
					no_count=no_count+1
					_file.write(str(tea.id)+',quiz_grade not present\n')                
				tea.mdlgrade=quiz_grade.grade
				tea.save()
				count = count + 1
			except:
				_file.write(str(tea.id)+',not updated\n')
				no_count=no_count+1

		_file.write('>> Script Completed. grades added, '+str(count)+'\n')
		_file.write('>> Script Completed. grades not added, '+str(no_count)+'\n')
		_file.close()    
		print(('>> Script Completed. grades added',count))
		print(('>> Script Completed. grades not added',no_count))