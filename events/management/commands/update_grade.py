from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from mdldjango.models import MdlUser, MdlQuizGrades
from events.models import *
from django.db import transaction as tx

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
	    print("hello")
	    quizstudents = MdlQuizGrades.objects.filter(quiz=47, grade__gte=98)

	    for mdlstudents in quizstudents:
	    	attendance = TestAttendance.objects.filter(mdluser_id = mdlstudents.userid, mdlquiz_id = 47)
	    	print(attendance)
	    	for att in attendance:
	    		print(att.id)
	    		att.grade = mdlstudents.grade
	    		att.save()




	    # 
	    # 	attendance = TestAttendance.objects.filter(mdluser_id = mdlstudents.userid)
	    	# 
	    	# 	att.grade = quizstudents.grade
	    	# 	quizstudents.save()


