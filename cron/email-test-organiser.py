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
organisers = Organiser.objects.all().exclude(academic__institution_type__id__in=[15,13,5])
sent = 0
notsent = 0
count = 0
tot_count = len(organisers)

subject = '"Invitation for Induction Training Programme"'

success_log_file_head = open(LOG_ROOT+'org-email-log.txt',"w")
for organiser in organisers:
    message = '''
Dear Sir/ Madam,

We are pleased to invite you to attend a 20-day residential programme for "Induction Training of Faculty" at IIT Bombay, from 28 November 2017 to 20 December 2017, between 9:00 am and 6:00 pm.

The Spoken Tutorial Project, under the aegis of Pandit Madan Mohan Malaviya National Mission on Teachers and Teaching (PMMMNMTT), is organising this residential programme to train 120 Teachers from Universities/Colleges/ Institutes, on various aspects of teaching and learning.  As per the decision by a Group of Secretaries of the Central Government, this is expected to become a mandatory training programme for new college teachers.

Please find enclosed our official invite letter. Request you to kindly circulate this amongst your friends and colleagues so that maximum no. of teachers can avail this opportunity.  

For more information please visit the following link.  
http://spoken-tutorial.org/induction

Thanks and regards,
Prof Kannan Moudgalya
IIT Bombay

'''.format(organiser.user.username)

    to  = [organiser.user.email]
    # to = ['ganeshmohite96@gmail.com','nancyvarkey@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'workshops@spoken-tutorial.org',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    #email.attach_alternative(html_content, "text/html")
    email.attach_file('/websites_dir/django_spoken/spoken/cron/Letter_for_training_faculty.pdf')
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
    # break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"

