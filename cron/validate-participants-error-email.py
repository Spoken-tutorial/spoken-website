
from builtins import str
from validate_email import validate_email
from DNS.Base import TimeoutError
import os, sys
import time

from config import *
# setting django environment
from django.core.wsgi import get_wsgi_application
sys.path.append(SPOKEN_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from events.models import Student

# fetching students needs to be verified
print('Initializing ...')
students = Student.objects.filter(error=True, verified__lt=3).order_by('-id')

# opening log files to write success & error attempts
today = time.strftime('%Y-%m-%d_%H-%M-%S')
success_log_file_head = open(LOG_ROOT+'validate-error-participants-success-log-'+today+'.txt',"w")
error_log_file_head = open(LOG_ROOT+'validate-error-participants-error-log-'+today+'.txt',"w")

for student in students:
  # default status message
  status = 'Invalid Format'

  # validating email format
  if validate_email(student.user.email):
    #student.verified = True
    try:
      # validating email existance
      if validate_email(student.user.email):
        student.user.is_active = True
        student.user.save()
        student.error = False
        student.verified = student.verified + 1
        student.save()
        status = 'Success'
        success_log_file_head.write(str(student.id)+','+str(student.user.id)+','+student.user.email+'\n')
      else:
        student.verified = student.verified + 1
        student.save()
        status = 'Not Available'
        error_log_file_head.write(str(student.id)+','+str(student.user.id)+','+student.user.email+'\n')
    except TimeoutError as e:
      error_log_file_head.write(str(student.id)+','+str(student.user.id)+','+student.user.email+'\n')
      print('Timeout error, waiting for 5 seconds...')
      time.sleep(3)
      continue
  print((student.user, '-', status))

error_log_file_head.close()
success_log_file_head.close()
