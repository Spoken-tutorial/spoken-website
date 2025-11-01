#code to send automated reminder mails to registerd users for activating their account
#to run this file please follow below instructions:
#1. Go to project directory
#2. run "python manage.py activation_reminder_mail >> cron/logs/reminder_mail_success_log.txt"



# Standard Library
import smtplib
import time
from datetime import date, datetime, timedelta

# Third Party Stuff
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.db import transaction as tx

# Spoken Tutorial Stuff
from cms.models import Profile


class Command(BaseCommand):

    @tx.atomic
    def handle(self, *args, **options):
        users = User.objects.filter(is_active = False, date_joined__gte = (datetime.now() - timedelta(days = 180)))
        today = datetime.now()
        sent = 0
        notsent = 0
        count = 0
        tot_count = len(users)
        subject = 'Gentle Reminder to activate the Spoken Tutorial account'
        
        for user in users:
          try:
            p = Profile.objects.get(user = user.id)
            if p != '':
              message = '''
                Dear {0} {1} ,

                Thank you for registering on {2}.
                This is a gentle reminder from Spoken Tutorial Team to activate your account. 
                Kindly activate your account by clicking on this link or copying and pasting it in your browser {3}

                Please ignore if you are already activated.
                Thank You.
                --
                Regards,
                Spoken Tutorial Team,
                IIT Bombay.'''.format(
                user.first_name, 
                user.last_name,
                "https://spoken-tutorial.org",
                "https://spoken-tutorial.org/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
                )
            to  = [user.email]
            email = EmailMultiAlternatives(
                subject, message, settings.NO_REPLY_EMAIL,
                to = to,
                headers = {
                 "Content-type" : "text/plain"
                }
            )
            count = count + 1
            try:
                result = email.send(fail_silently=False)
                sent += 1
                print((str(user.id),',', str(user.email),',', str(1)))
            except smtplib.SMTPException:
                print('Error: Unable to send email')
                notsent += 1
                print((str(user.id),',', str(user.email),',', str(0)))
          except  ObjectDoesNotExist as e:
              print(('no profile : ',user.id,',',e))
        #for loop ends here
        print('--------------------------------')
        print(('Date : ', today))
        print(('Total sent mails: ', sent))
        print(('Total not sent mails: ', notsent))
        print('--------------------------------')
