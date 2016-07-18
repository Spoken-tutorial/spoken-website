import time
import os, sys
from django.db.models import Q

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
organisers = Organiser.objects.filter(status=1).exclude(academic__institution_type__id__in=[14,13,5])
sent = 0
notsent = 0
count = 0
tot_count = len(organisers)

subject = '"Higher-Ed Summit at IIT Bombay, Feb 18th 2016"'

success_log_file_head = open(LOG_ROOT+'drupal-org-email-log.txt',"w")
for organiser in organisers:
    message = '''
Dear Academic Lead,

We invite you to join the Drupal Higher-Ed Summit to be held in Mumbai on 18th Feb 2016. The event focuses on the Drupal and Open Source in Education.
Kindly find the attached documents to Register for the event and to collect more information related this event.

Thank You.


Regards
Administrator
Spoken Tutorial Project
IIT Bombay'''.format(organiser.user.username)

    #to  = [organiser.user.email]
    to = ['rachit.gupta@drupalmumbai.org','rakhi.mandhania@qed42.com','mukesh.agarwal@innoraft.com','kirti3192@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    #email.attach_alternative(html_content, "text/html")
    email.attach_file('/websites_dir/django_spoken/spoken/cron/ProgramDetails.pdf')
    email.attach_file('/websites_dir/django_spoken/spoken/cron/Register.html')
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

