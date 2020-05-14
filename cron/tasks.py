from __future__ import absolute_import, unicode_literals
from spoken.config import *
from celery import shared_task
from .models import AsyncCronMail
import csv
from builtins import str
import time
import os, sys
from datetime import datetime  
from django.utils import timezone
from django.conf import settings
import uuid
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from smtplib import SMTPException, SMTPServerDisconnected
from django.core.mail import BadHeaderError

@shared_task
def async_bulk_email(taskid, *args, **kwargs):
    sent=0
    errors=0
    task = AsyncCronMail.objects.get(pk=taskid)
    log_file_name = 'log_email_'+uuid.uuid4().hex+".csv"
    log_file=open(settings.CRON_ROOT + log_file_name, "w+")
    with open(task.csvfile.path, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in csvreader:
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
                log_file.write(str(row[0])+','+str(1)+'\n')
            except ValidationError as mail_error:
                log_file.write(str(row[0])+','+str(0)+','+str(mail_error)+'\n')
                errors+=1
            except SMTPException as send_error:
                log_file.write(str(row[0])+','+str(0)+','+str('SMTP mail send error.')+'\n')
                errors+=1
            except BadHeaderError as header_error:
                log_file.write(str(row[0])+','+str(0)+','+str(header_error)+'\n')
                errors+=1
            except ConnectionRefusedError as refused:
                log_file.write(str(row[0])+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
                errors+=1
            except SMTPServerDisconnected as disconnect:
                log_file.write(str(row[0])+','+str(0)+','+str('Failed to connect to SMTP server.')+'\n')
                errors+=1
        
        task.log_file.name = 'emails/' + log_file_name
        task.completed_at = timezone.now()
        task.report = "Total: "+ str(sent+errors)+"\n"+ "Sent: "\
                +str(sent)+"\n"+"Errors: "+ str(errors)
        task.status=True
        task.save()
        log_file.close()


