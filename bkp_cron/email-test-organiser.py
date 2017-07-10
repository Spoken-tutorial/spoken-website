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
organisers = Organiser.objects.filter(status=1)
sent = 0
notsent = 0
count = 0
tot_count = len(organisers)

subject = '"IITBombayX MOOCs course on "Basic 3D animation using Blender"'

success_log_file_head = open(LOG_ROOT+'animation-org-email-log.txt',"w")
for organiser in organisers:
    message = '''

Dear Organiser,

IITBombayX is offering a new MOOCs course on "Basic 3D animation using Blender". 
Please forward this poster to the students/faculty who would benefit!

Also attached is a letter from Prof. Phatak, IIT Bombay, explaining what is a MOOC.

Regards
Spoken Tutorial Team
IIT Bombay'''.format(organiser.user.username)

    to  = [organiser.user.email]
    #to = ['k.sanmugam2@gmail.com', 'kirti3192@gmail.com', 'nancyvarkey@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    #email.attach_alternative(html_content, "text/html")
    email.attach_file('/websites_dir/django_spoken/spoken/cron/SKANI_Letter_DBP.pdf')
    email.attach_file('/websites_dir/django_spoken/spoken/cron/SKANI_Jan2016_Poster.pdf')
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
    #break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"

