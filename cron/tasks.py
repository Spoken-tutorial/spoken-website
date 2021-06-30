from __future__ import absolute_import, unicode_literals
import csv
from builtins import str
import time
import os, sys
# setting django environment
from django.core.wsgi import get_wsgi_application
from config import *
sys.path.append(SPOKEN_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from .models import AsyncCronMail
from datetime import datetime  
from django.utils import timezone
from django.conf import settings
import uuid
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from smtplib import SMTPException, SMTPServerDisconnected
from django.core.mail import BadHeaderError
from rq.decorators import job
from cron import REDIS_CLIENT, DEFAULT_QUEUE, TOPPER_QUEUE
from rq import Retry
import time
from rq import get_current_job
from django.core.cache import caches
from mdldjango.models import MdlUser, MdlQuizGrades
from events.models import FossMdlCourses, TestAttendance, State, City, InstituteType
from creation.models import FossCategory

def bulk_email(taskid, *args, **kwargs):
    task = AsyncCronMail.objects.get(pk=taskid)
    if  task.log_file.name == "":
        log_file_name = 'log_email_'+uuid.uuid4().hex+".csv"
        task.log_file.name = 'emails/' + log_file_name
        task.save()
    with open(settings.MEDIA_ROOT + task.log_file.name, "a") as log_file:
        with open(task.csvfile.path, newline='') as csvfile:
            csvreader = list(csv.reader(csvfile, delimiter=' ', quotechar='|'))
            job = get_current_job()
            try:
                row_id=int(job.meta['row_id'])
            except:
                row_id =0
            try:
                sent=int(job.meta['sent'])
            except:
                sent=0
            try:
                errors=int(job.meta['errors'])
            except:
                errors=0
            for i,row in enumerate(csvreader[row_id:], row_id):
                job.meta['row_id'] = i
                job.save_meta()
                if len(row) < 1:
                    continue
                if i%10 == 0:
                        print('Total ran: ',i)
                        time.sleep(5)
                email = EmailMultiAlternatives(
                            task.subject, task.message, task.sender,
                            to = [row[0]],
                            headers = {
                                        "Content-type" : "text/html"
                                    }
                        )
                try:
                    validate_email(row[0])
                    email.attach_alternative(task.message, "text/html")
                    email.send()
                    sent += 1
                    job.meta['sent'] = sent
                    job.save_meta()
                    log_file.write(str(row[0])+','+str(1)+'\n')
                except ValidationError as mail_error:
                    log_file.write(str(row[0])+','+str(0)+','+str(mail_error)+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()
                except SMTPException as send_error:
                    log_file.write(str(row[0])+','+str(0)+','+str('SMTP mail send error.')+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()
                except BadHeaderError as header_error:
                    log_file.write(str(row[0])+','+str(0)+','+str(header_error)+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()
                except ConnectionRefusedError as refused:
                    log_file.write(str(row[0])+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
                    errors+=1
                except SMTPServerDisconnected as disconnect:
                    log_file.write(str(row[0])+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()
                except OSError as e:
                    log_file.write(str(row[0])+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
                    errors+=1
                    job.meta['errors'] = errors
                    job.save_meta()

            task.completed_at = timezone.now()
            task.report = "Total: "+ str(sent+errors)+"\n"+ "Sent: "\
                    +str(sent)+"\n"+"Errors: "+ str(errors)
            task.status=True
            task.save()

def async_bulk_email(task, *args, **kwargs):
    DEFAULT_QUEUE.enqueue(bulk_email, task.pk, job_id=task.job_id, job_timeout='72h')


def filter_student_grades(key=None):
  key_array=key.split(':')
  foss=FossCategory.objects.filter(pk__in=[int(f) for f in key_array[0].split(';')])
  state=State.objects.filter(pk__in=[int(s) if s != '' else None  for s in key_array[1].split(';')])
  city=City.objects.filter(pk__in=[int(c) if c != '' else None for c in key_array[2].split(';')])
  institution_type=InstituteType.objects.filter(pk__in=[int(i) if i != '' else None for i in key_array[4].split(';')])
  grade=int(key_array[3])
  activation_status=int(key_array[5]) if key_array[5]!= '' else None
  from_date= key_array[6] if key_array[6] != 'None' else None
  to_date= key_array[7] if key_array[7] != 'None' else None
  if grade:
    #get the moodle id for the foss
    try:
      fossmdl=FossMdlCourses.objects.filter(foss__in=foss)
      #get moodle user grade for a specific foss quiz id having certain grade
      if from_date and to_date:
        user_grade=MdlQuizGrades.objects.using('moodle').values_list('userid', 'quiz', 'grade').filter(quiz__in=[f.mdlquiz_id for f in fossmdl], grade__gte=int(grade), timemodified__range=[datetime.strptime(from_date,"%Y-%m-%d").timestamp(), datetime.strptime(to_date,"%Y-%m-%d").timestamp()])
      elif from_date:
        user_grade=MdlQuizGrades.objects.using('moodle').values_list('userid', 'quiz', 'grade').filter(quiz__in=[f.mdlquiz_id for f in fossmdl], grade__gte=int(grade), timemodified__gte=datetime.strptime(from_date,"%Y-%m-%d").timestamp())

      #convert moodle user and grades as key value pairs
      dictgrade = {i[0]:{i[1]:[i[2],False]} for i in user_grade}
      #get all test attendance for moodle user ids and for a specific moodle quiz ids
      test_attendance=TestAttendance.objects.filter(
                                mdluser_id__in=list(dictgrade.keys()), 
                                mdlquiz_id__in=[f.mdlquiz_id for f in fossmdl], 
                                test__academic__state__in=state if state else State.objects.all(),
                                test__academic__city__in=city if city else City.objects.all(), 
                                status__gte=3, 
                                test__academic__institution_type__in=institution_type if institution_type else InstituteType.objects.all(), 
                                test__academic__status__in=[activation_status] if activation_status else [1,3]
                              )
        
      filter_ta=[]
      for i in range(test_attendance.count()):
        if not dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1]:
          dictgrade[test_attendance[i].mdluser_id][test_attendance[i].mdlquiz_id][1] = True
          filter_ta.append(test_attendance[i])
          
      #return the result as dict
      result= {'mdl_user_grade': dictgrade, 'test_attendance': filter_ta, "count":len(filter_ta)}
      caches['file_cache'].set(key,result)
      if not TOPPER_WORKER_STATUS:
          return result
    except FossMdlCourses.DoesNotExist:
      return None
  return None


def async_filter_student_grades(key):
    TOPPER_QUEUE.enqueue(filter_student_grades, key, job_id=key, job_timeout='72h')