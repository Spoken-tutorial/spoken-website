
from datetime import datetime, date, timedelta
from django.db.models import Q
import os, sys
import MySQLdb
import time

# setting django environment
from django.core.wsgi import get_wsgi_application
from config import *
sys.path.append(SPOKEN_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

# importing config and TrainingRequest
from events.models import Test

test_requests = Test.objects.filter(status=4).order_by('-created')

for test in test_requests:
  participant_count = int(test.participant_count)
  attendance_count = int(test.get_test_attendance_count())
  if attendance_count > 0:
    if not participant_count == attendance_count:
      print((test.id, participant_count, attendance_count))
      test.update_test_participant_count()
