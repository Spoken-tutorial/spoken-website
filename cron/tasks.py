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
                result = email.send()
                sent += 1
                if sent%100==0:
                    time.sleep(10)
                log_file.write(str(row[0])+','+str(1)+'\n')
            except Exception as e:
                log_file.write(str(row[0])+','+str(0)+'\n')
                errors+=1
        
        task.log_file.name = 'emails/' + log_file_name
        task.completed_at = timezone.now()
        task.report = "Total mails count: "+ str(sent+errors)+"\n"+ "Mails sent: "\
                +str(sent)+"\n"+"Errors: "+ str(errors)
        task.status=True
        task.save()
        log_file.close()


