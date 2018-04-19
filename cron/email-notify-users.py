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
from events.models import Drupal2018_email

#here fetch all user
users = Drupal2018_email.objects.all()
sent = 0
notsent = 0
count = 0
tot_count = len(users)

subject = ' Invitation to attend "Drupal in a Day" workshop'

success_log_file_head = open(LOG_ROOT+'drupal2018_org_invitation.txt',"w")
for user in users:
    message = '''
<p>Dear Future Professionals,</p>

<p>Spoken Tutorial in association with FOSSEE, IIT Bombay, is hosting "Drupal-in-a-Day" workshop alongside Drupal Camp Mumbai 2018 at IIT Bombay. We invite you to attend this workshop and learn Drupal, the world\'s leading open source content management framework, for developing websites and web based applications (for desktop and mobile). On successful completion of the surprise activity, you also stand a good chance to get a free participation ticket to attend two days of Drupal Camp on 28 and 29 April 2018.</p>

<p>Drupal Camp Mumbai is one of the largest Drupal community gatherings in India. The purpose of this event is to bring students, developers, architects, managers, businesses and organisations on a singular platform to network, interact and share openly with each other, and help strengthen the community at large.</p>

<p>The training workshop is focused self-learning and real time practising model, where each student will be provided with high quality video tutorials developed by Spoken Tutorial projcet and at the end of the workshop the student should be able to build a full fledged Drupal-based website.</p>

<p>Come learn, be a part of the largest open source community for web content management, and hone your skills to an exciting career in web applications.</p>

<p><b>When:-</b> 27 April 2018 <br>

<b>Venue:-</b> Seminar Room, Ground Floor, Aero Annex Building, Below HSS Department, IIT Bombay, Mumbai 400076.

<br><b>To know more and Register:-</b> <a href="http://spoken-tutorial.org/workshop/drupal2018/" target="_blank">Click Here</a></p>

<p>Thanks and rgds,<br>
Tejas Shah, Organising Team<br>
Spoken Tutorial, FOSSEE and DCM<br>
IIT Bombay</p>

'''.format(user.email)

    to  = [user.email]
    #to = ['ganeshmohite96@gmail.com','nancyvarkey.iitb@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'tejas.shah@iitb.ac.in',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    email.attach_alternative(message, "text/html")
    # email.attach_file('/websites_dir/django_spoken/spoken/cron/collegeletter.pdf')
    count = count + 1
    try:
        result = email.send(fail_silently=False)
        sent += 1
        if sent%100 == 0:
            time.sleep(10)
        #print to," => sent (", str(count),"/",str(tot_count),")"
        success_log_file_head.write(str(user.email)+','+str(1)+'\n')
    except Exception, e:
        print e
        #print to," => not sent (",count,"/",tot_count,")"
        success_log_file_head.write(str(user.email)+','+str(0)+'\n')
    #break
print "--------------------------------"
print tot_count
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"
