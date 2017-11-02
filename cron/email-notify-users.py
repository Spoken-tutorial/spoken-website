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
from events.models import InductionInterest

#here fetch all user
users = InductionInterest.objects.filter(
    (Q(age ='20to25') | Q(age = '26to30') | Q(age = '31to35')),
    (Q(experience_in_college = 'Lessthan1year') | Q(experience_in_college = 'Morethan1yearbutlessthan2years'))
    ).exclude(designation = 'Other').values_list('email',flat=True).distinct()
sent = 0
notsent = 0
count = 0
tot_count = len(users)

subject = '"Reminder to complete and submit your assignment "'

success_log_file_head = open(LOG_ROOT+'induction_particiants_reminder.txt',"w")
for user in users:
    message = '''
Dear Participant,

This is to remind you that the last date of submission of assignment is 3 November 2017, 5 p.m.  You have to complete all 3 Knack games - Bomba Blitz, Meta Maze and Dashi Dash,  in order for your profile and score to be generated on our interface.  You also have to use the Knack code sent to you in your registered email id.


If you have already done so, pls ignore this mail.


But if you have not done so, pls complete the assignment before the deadline mentioned above.

Regards,
Organising Team
Induction Training Programme
IIT Bombay

'''.format(user)

    to  = [user]
    # to = ['ganeshmohite96@gmail.com','nancyvarkey@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'workshops@spoken-tutorial.org',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    #email.attach_alternative(html_content, "text/html")
    # email.attach_file('/websites_dir/django_spoken/spoken/cron/Knack-user-flow.pdf')
    count = count + 1
    try:
        result = email.send(fail_silently=False)
        sent += 1
        if sent%100 == 0:
            time.sleep(10)
        #print to," => sent (", str(count),"/",str(tot_count),")"
        success_log_file_head.write(str(user)+','+str(1)+'\n')
    except Exception, e:
        print e
        #print to," => not sent (",count,"/",tot_count,")"
        success_log_file_head.write(str(user)+','+str(0)+'\n')
    # break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"
