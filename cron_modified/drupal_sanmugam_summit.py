import time
import os, sys
from django.db.models import Q
from django.template.loader import get_template

# setting django environment
from django.core.wsgi import get_wsgi_application
sys.path.append("/websites_dir/django_spoken/spoken")
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from config import *
from cms.models import *
from events.models import Organiser

#here fetch all organisers in user
organisers = Organiser.objects.filter(status=1)
sent = 0
notsent = 0
count = 0
tot_count = len(organisers)

subject = '"Higher-Ed Summit at IIT Bombay, Feb 18th 2016"'

msg_plain = get_template('/websites_dir/django_spoken/spoken/cron/emailtemplate/mailtpl.txt')
msg_html = get_template('/websites_dir/django_spoken/spoken/cron/emailtemplate/mailtpl.html')


success_log_file_head = open(LOG_ROOT+'drupal-org-email-log.txt',"w")
for organiser in organisers:

    #to  = [organiser.user.email]
    #to = ['k.sanmugam2@gmail.com']
    to = ['kirti3192@gmail.com']
    email = EmailMultiAlternatives(
        subject, msg_plain, 'administrator@spoken-tutorial.org',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    email.attach_alternative(msg_html, "text/html")
    #email.attach_file('/websites_dir/django_spoken/spoken/cron/ProgramDetails.pdf')
    #email.attach_file('/websites_dir/django_spoken/spoken/cron/SKANI_Jan2016_Poster.pdf')
    count = count + 1
    try:
        result = email.send(fail_silently=False)
        sent += 1
        if sent%100 == 0:
            time.sleep(10)
        #print to," => sent (", str(count),"/",str(tot_count),")"
        success_log_file_head.write(str(organiser.id)+','+str(1)+'\n')
    except Exception, e:
        print e
        #print to," => not sent (",count,"/",tot_count,")"
        success_log_file_head.write(str(organiser.id)+','+str(0)+'\n')
    break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"

