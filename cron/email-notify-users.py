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
from events.models import Organiser, AcademicCenter

#here fetch all user
organisers = Organiser.objects.exclude(academic__institution_type_id__in=[3,2,15,5,13,4])
sent = 0
notsent = 0
count = 0
tot_count = len(organisers)

subject = ' *IIT Bombay - Spoken Tutorial Program | Invitation to colleges for 2019* '

success_log_file_head = open(LOG_ROOT+'organiser_payment_reminder.txt',"w")
for organiser in organisers:
    message = '''
<p>Dear Faculty Organiser,<p>

<p>Many thanks to you and your College for being a part of the IIT Bombay,Spoken Tutorial Software training program. You have contributed in a great way to its mega success. <p>

<p>In August 2018 we informed you about the Training Policy change namely colleges will need to make a Payment/annual User fee of Rs.25000/- in order to continue the Spoken Tutorial Training. Many of you have immediately responded positively and made the payment. <u>To continue to benefit from the Software Training courses we offer - Payment is a must.  </u> </p>

<p>We wish to inform you that we have moved to a continual payment system wherein <b><u>Colleges get a full 12 months benefit from their date of payment. Eg. Jan 28th 2019 to Jan 27th 2020 etc.  </u></b> I would urge all colleges who are not in the program to come in and see what benefits they are getting for Rs.25000/-. There is NO OTHER course with this standard, this level of flexibilty and at this low cost per student.</p>

<p>One consideration from our end is related to the Test taking - Colleges who had done tests but were unable to download the certificates because colleges were disabled, we will activate those colleges for a short period of time, so that you can download the students certificates. For this you can contact your state training managers.</p>

<p>We guarantee our continued high-quality services to all. If you have questions, don't hesitate to contact the Training Coordinator of your respective state.</p>

<p><b>Yours Sincerely, <br>
Shyama Iyer <br>
National Coordinator - Training Spoken Tutorial, IIT Bombay <br>
NMEICT, MHRD, Govt. Of India<br>
</b></p>

'''.format(organiser.user.email)

    to  = [organiser.user.email]
    #to = ['ganeshmohite96@gmail.com','nancyvarkey.iitb@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
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
        success_log_file_head.write(str(organiser.user.email)+','+str(1)+'\n')
    except Exception, e:
        print e
        #print to," => not sent (",count,"/",tot_count,")"
        success_log_file_head.write(str(organiser.user.email)+','+str(0)+'\n')
    #break
print "--------------------------------"
print tot_count
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"
