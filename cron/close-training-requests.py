from datetime import datetime, date, timedelta
from django.db.models import Q
import os, sys
import MySQLdb
import time

# setting django environment
from django.core.wsgi import get_wsgi_application
sys.path.append("/websites_dir/django_spoken/spoken")
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

# importing config and TrainingRequest
from config import *
from events.models import TrainingRequest

# today's date
today = date.today()

# fetching all training requests needs to closed
training_requests = TrainingRequest.objects.filter(
  Q(sem_start_date__lte=datetime.now()-timedelta(days=150)), \
  status=0
)

# opening log file to keep details of updated records
today = time.strftime('%Y-%m-%d_%H-%M-%S')
success_log_file_head = open(LOG_ROOT+'close-training-requests-success-log-'+today+'.txt',"w")

for training_request in training_requests:
  # updating participant's count
  participant_count = training_request.update_participants_count()
  success_log_file_head.write(str(training_request.id)+','+str(participant_count)+'\n')

success_log_file_head.close()

count = training_requests.count()

#updating training request status
training_requests.update(status=1)

print '*************************************'
print ' Total records checked: ', count
print '*************************************'
