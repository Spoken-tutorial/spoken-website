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
from cron import REDIS_CLIENT, DEFAULT_QUEUE
from rq import Retry
import time
from rq import get_current_job

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
    print('working')