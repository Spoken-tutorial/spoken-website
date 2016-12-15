import time
import os, sys
from datetime import datetime, date, timedelta
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

users = User.objects.filter(is_active = 0, date_joined__lte=(datetime.now()-timedelta(days=7)))
sent = 0
notsent = 0
count = 0
tot_count = len(users)
print 'users not activated yet : ',tot_count
subject = 'Gentle Reminder to activate the Spoken Tutorial account'
success_log_file_head = open(LOG_ROOT+'activation_reminder_mail_success_list.txt',"w")
fail_log_file_head = open(LOG_ROOT+'activation_reminder_mail_fail_list.txt',"w")
for user in users:
    message = '''
Dear User,

Thank you for registering on Spoken Tutorial website.
This is a gentle reminder from Spoken Tutorial Team to activate your account. 
Kindly activate your account by clicking on the activation link which has been sent to you at the time of registration.
If you have not received any activation mail from Spoken Tutorial website, kindly contact respective Training Manager.

Please ignore if you are already activated.
Thank You.
--
Regards,
Spoken Tutorial Team,
IIT Bombay.'''.format(user.username)

    to  = [user.email]
    #to = ['kirti@cse.iitb.ac.in']
    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    count = count + 1
    try:
        result = email.send(fail_silently=False)
        sent += 1
        if sent%100 == 0:
            time.sleep(10)
        success_log_file_head.write(str(user.id)+','+str(user.email)+','+str(1)+'\n')
    except Exception, e:
        print e
        notsent += 1
        fail_log_file_head.write(str(user.id)+','+str(user.email)+','+str(0)+'\n')
    #break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"
