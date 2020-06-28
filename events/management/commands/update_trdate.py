
# Third Party Stuff
from django.core.management.base import BaseCommand
from django.db import transaction as tx
from datetime import datetime,timedelta
from django.utils import timezone
from django.db.models import Q
from events.models import *

class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
    	print('>> adding tr dates in TrainingRequest')
    	count =0
    	training_rqs = TrainingRequest.objects.all()
    	for trreq in training_rqs:
    		sem_date = trreq.sem_start_date.strftime('%Y-%m-%d')
    		date = datetime.strptime(sem_date, "%Y-%m-%d").date()

    		semtype = trreq.training_planner.semester_id

    		#odd - july to dec = 2
    		#even - Jan to June = 1
    		trreq.training_start_date = trreq.sem_start_date
    		if semtype == 1:
    			trreq.training_end_date = str(date.year)+'-06-30'
    		if semtype == 2:
    			trreq.training_end_date = str(date.year)+'-12-31'
    		trreq.save()
    		count = count + 1
    	print(('>> Script Completed. date added',count))
