from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from mdldjango.models import MdlUser, MdlQuizGrades
from events.models import *
from django.db import transaction as tx

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
	    print("hello")
	    fossquizlist = [47,10,42,70,46,62,88,93,100,99,94,52,61,8]
	    quizstudents = MdlQuizGrades.objects.filter(grade__gte=50, quiz__in=fossquizlist)

	    for mdlstudents in quizstudents:
	    	attendance = TestAttendance.objects.filter(mdluser_id = mdlstudents.userid, mdlquiz_id__in=fossquizlist)
	    	print(attendance)
	    	for att in attendance:
	    		print(att.id)
	    		att.grade = mdlstudents.grade
	    		att.save()




