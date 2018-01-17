from django.db.models import Q
import os, sys
import MySQLdb
import time

# setting django environment
from django.core.wsgi import get_wsgi_application
sys.path.append("/websites_dir/django_spoken/spoken")
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from config import *
from creation.models import TutorialResource, PublishTutorialLog

with open(LOG_ROOT+'publish_date_log.txt',"w") as success_log_file_head:
	count =0 

	tutorials = TutorialResource.objects.all()
	for tutorial in tutorials:
		count = count + 1
		try:
			latest_publish_date = PublishTutorialLog.objects.filter(tutorial_resource_id = tutorial.id).order_by('-id').first()
			if latest_publish_date:
				tutorial.publish_date = latest_publish_date.created
			else :
				tutorial.publish_date = tutorial.created
			tutorial.save()		
			success_log_file_head.write(str(tutorial.id)+','+str(1)+'\n')
		except Exception, e:
			print e
			success_log_file_head.write(str(tutorial.id)+','+str(0)+'\n')
	success_log_file_head.write('------- tutorials publish date updated ---------- :'+str(count))
