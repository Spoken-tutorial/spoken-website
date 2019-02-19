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

#here fetch all user
users = Organiser.objects.filter(status=1)
sent = 0
notsent = 0
count = 0
tot_count = len(users)

subject = ' Spoken Tutorial, IIT Bombay - Change in Training Policy'

success_log_file_head = open(LOG_ROOT+'organiser_charge_list.txt',"w")
for user in users:
    message = '''
<p>
Dear Faculty Organiser,
</p>

<p>
We are truly happy to be associated with you as a Knowledge Partner for the past few years.  We provided Spoken Tutorial Software/ IT Courses training in your college and have grown together. The team at IIT Bombay has continued to offer new and exotic courses of world class quality, so essential for our students to get an employability worthy Skill Set. 
</p>

<p>
The new academic year will start soon - this is the right time to plan. You have already submitted planners & calendars in advance, covering the next 2 semesters. Be assured we will be with you all the way guiding, enabling & enhancing the quality of our delivery. In this connection, I wish to inform you of a policy change that has come to us from MHRD Govt. Of India. <u>Effective July, 2018 we are expected to charge a nominal annual amount from the colleges we are working with.</u> This decision has been driven by the fact that we are a mature and successful program, therefore from now on need to generate revenue and sustain our Project financially, on our own. The amount is <b><i>Rs. 25,000 per year</i></b> to be paid by colleges for an unlimited number of Training Workshops & Certification Tests taken by any number of their students & staff. There is no upper limit. Note also, we will not charge anything to colleges who have just come into the program and might train less than 100 students in a year.
</p>

<p>
We did extensive enquiries with our Engg., as well as Arts, Science, Commerce colleges and found out pleasantly that this amount was very manageable. In fact, considering a simple calculation for providing Basic Computer Skills - say getting our LibreOffice package training with Certificates of Word Processing, Spreadsheet & Slide presentation  at Rs.200/ student - just for 125 students the amount works out to a total of Rs. 25000/year/college. Most of you will be training 100s of students as you move to additional courses and more departments. You will roll out our Drupal, OpenFOAM, Java, C/C++, PHP, Linux, GIT and many other lucrative courses. Certainly it is tremendous value for money. At the outset, this news could come as a surprise, as till now, the Spoken Tutorial training programs were free of cost. But it is my belief that this move will be accepted in a positive way. 
</p>

<p><b>The Information Module & Payment Link on our website will be live in July</b>, and we will keep you informed. In the meanwhile - 
<ol>
    <li>Please discuss with your management Principal/ Director/ VC et al. about the policy change.</li>
    <li>After approval/permission, please send us the name & contact details of the point person in your college who will access the payment link and take care of the financial transaction. This person will mostly be from the Accounts/Finance section of your college.</li>
</ol></p>
<p>Do drop a mail immediately to your respective state Training Coordinator, informing them of your college's decision, so we can proceed with the training. We guarantee our continued high quality services to all. If you have questions, don't hesitate to contact the Training Coordinator of your respective state.</p>
<p>Yours Sincerely, <br><br>

Shyama Iyer<br>
National Coordinator - Training<br>
Spoken Tutorial, IIT Bombay<br>
NMEICT, MHRD, Govt. Of India<br>
</p>

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
    except Exception as e:
        print(e)
        #print to," => not sent (",count,"/",tot_count,")"
        success_log_file_head.write(str(organiser.user.email)+','+str(0)+'\n')
    #break
print("--------------------------------")
print(tot_count)
print("Total sent mails:", sent)
print("Total not sent mails:", notsent)
print("--------------------------------")
