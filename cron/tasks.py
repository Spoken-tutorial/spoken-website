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

@shared_task
def async_bulk_email(taskid, *args, **kwargs):
    sent=0
    errors=0
    task = AsyncCronMail.objects.get(pk=taskid)
    log_file=open(settings.CRON_ROOT+'log_email_'+uuid.uuid4().hex+".csv", "w+")
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
                email.attach_alternative(task.message, "text/html")
                result = email.send()
                sent += 1
                if sent%100==0:
                    time.sleep(10)
                log_file.write(str(row[0])+','+str(1)+'\n')
            except Exception as e:
                log_file.write(str(row[0])+','+str(0)+'\n')
                errors+=1

        log_file.close()
        task.completed_at = timezone.now()
        task.report = "Total mails count: "+ str(sent+errors)+"\n"+ "Mails sent: "\
                +str(sent)+"\n"+"Errors: "+ str(errors)
        task.status=True
        task.save()


