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

organisers = Organiser.objects.filter(status=1)
sent = 0
notsent = 0
count = 0
tot_count = len(organisers)

subject = 'Reminder Mail _ Spoken Tutorials IIT Bombay | Timely marking of the Participant List (PL)'

success_log_file_head = open(LOG_ROOT+'organiser_pl_marking_reminder_log.txt',"w")
for organiser in organisers:
    message = '''

Dear Faculty Organisers,

The Spoken Tutorial team can see that you are very good in systematically planning and conducting the training session for your students.

You have followed all the regular processes till date namely by -

1.uploading your student nominal roll (i.e) Master Batche(s),
2.selected appropriate courses by filling the semester training planner (STP) through your organiser login on http://spoken-tutorial.org

IMPORTANT- Now, it is time for you to mark attendance (i.e) complete STEP 3 of the Semester Training Planner Summary (STPS); "Mark the Participant List (PL)" to complete the process.



This is your next immediate activity (to be completed by December 29, 2017)...
Log-on to http://spoken-tutorial.org
Goto 'Software Training' >> 'Training Dashboard' >> 'Semester Training Planner Summary' >> 'STEP 3 : Select Participant List' --- mark attendance for all batches listed one by one.
for more details:http://process.spoken-tutorial.org/images/1/1c/Select_Participantlist.pdf



Why Mark PL?

Any course that your student take for which (MB) batches are enrolled and courses marked (STP), has to be formally endorsed by you as an Organiser. Without completing PL, the students won't be able to take any Online Test or receive any Certificate(s).


So hurry ! last date for marking the PL (for the selected courses) has been extended till December 29, 2017.


Here's wishing you the best and guaranteeing our continued support for offering the Spoken Tutorial Software training to all. If you have questions, please contact the Training Coordinator of your respective state.


Best wishes,

Shyama Iyer
National Coordinator - Training
Spoken Tutorial, IIT Bombay


'''.format(organiser.user.email)

    to  = [organiser.user.email]
    # to = ['ganeshmohite96@gmail.com','nancyvarkey@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
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
        success_log_file_head.write(str(organiser.user.email)+','+str(1)+'\n')
    except Exception, e:
        print e
        #print to," => not sent (",count,"/",tot_count,")"
        success_log_file_head.write(str(organiser.user.email)+','+str(0)+'\n')
    # break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"

