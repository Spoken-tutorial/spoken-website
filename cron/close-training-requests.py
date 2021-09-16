
from builtins import str
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
from events.models import TrainingRequest

# today's date
today = date.today()

# fetching all training requests needs to closed
training_requests = TrainingRequest.objects.filter(
  Q(sem_start_date__lte=datetime.now()-timedelta(days=30)), \
  status=0
)

# opening log file to keep details of updated records
today = time.strftime('%Y-%m-%d_%H-%M-%S')
success_log_file_head = open(LOG_ROOT+'close-training-requests-success-log-'+today+'.txt',"w")

for training_request in training_requests:
  # updating participant's count
  participant_count = training_request.update_participants_count()
  # Training close automatically if participant count exists
  if participant_count:
    training_request.status = 1
    training_request.cert_status = 0
    training_request.save()
  success_log_file_head.write(str(training_request.id)+','+str(participant_count)+'\n')

success_log_file_head.close()

count = training_requests.count()

#updating training request status
#training_requests.update(status=1)

print('*************************************')
print((' Total records checked: ', count))
print('*************************************')
