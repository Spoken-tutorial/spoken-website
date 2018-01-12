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
from events.models import InductionInterest, InductionFinalList

#here fetch all user
users = InductionFinalList.objects.filter(batch_code='20171103')
sent = 0
notsent = 0
count = 0
tot_count = len(users)

subject = ' Reminder: "Instructions for uploading the college letter and paying the registration fee" '

success_log_file_head = open(LOG_ROOT+'induction_particiants_thirdshortlist.txt',"w")
for user in users:
    message = '''
Dear Candidate,

This email is a reminder for you to upload the certificate requested in our last email and make the payment of non-refundable course fees of Rs.1000.  Both of these tasks should be completed by 16 November 2017. The certificate should be on the College Letterhead and should be exactly as per the proforma, which we sent as an attachment in the previous email.

We would appreciate your urgent attention to this matter and look forward to receiving the same, no later than the date mentioned above.   So, kindly do so at the earliest.  

After the stipulated deadline, we will have to release your seat for the candidates in the next shortlist, if our records show that you have not done either of the above.

If you have already completed both the above steps, kindly ignore this mail.


Thanks and rgds,
Organising Team
PMMMNMTT Induction Training Programme
IIT Bombay




'''.format(user.email)

    to  = [user.email]
    # to = ['ganeshmohite96@gmail.com','nancyvarkey@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'workshops@spoken-tutorial.org',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    #email.attach_alternative(html_content, "text/html")
    email.attach_file('/websites_dir/django_spoken/spoken/cron/collegeletter.pdf')
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
    # break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"
