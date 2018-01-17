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

tutorials = TutorialResource.objects.all()
for tutorial in tutorials:
	latest_publish_date = PublishTutorialLog.objects.filter(tutorial_resource_id = tutorial.id).order_by('-id').first()
	if latest_publish_date:
		tutorial.publish_date = latest_publish_date.created
	else :
		tutorial.publish_date = tutorial.created
	tutorial.save()

