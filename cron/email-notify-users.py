
from builtins import str
import time
import os, sys
from django.db.models import Q

# setting django environment
from django.core.wsgi import get_wsgi_application
from config import *
sys.path.append(SPOKEN_PATH)
os.environ["DJANGO_SETTINGS_MODULE"] = "spoken.settings"
application = get_wsgi_application()

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
 
from cms.models import *
from events.models import Organiser, AcademicCenter

#here fetch all user
organisers = Organiser.objects.exclude(academic__institution_type_id__in=[3,2,15,5,13,4])
sent = 0
notsent = 0
count = 0
tot_count = len(organisers)

subject = ' *Automated Mail _ IIT Bombay Spoken Tutorials | Renewal of Subscription* '

success_log_file_head = open(LOG_ROOT+'organiser_payment_renewal.txt',"w")
for organiser in organisers:
    message = '''
<p>Dear Faculty Organiser,<p>

<p>
Thank you for the continuing to offer the Spoken Tutorial Training sessions in this academic year in your college. You have contributed in a great way to the project's success. You are now organising training sessions, planning for tests, motivating faculty from other departments to take these courses to their students and completing the processes for the same. We are with you to guide and support so that maximum students in your college avail of the Training.
</p>

<p>
<b>
Please note that your college's annual Subscription fee validity is expiring shortly. Without any delay ensure that the fee renewal process for Year 2 is completed. We will continue to keep your Login activated. Payment stays Rs.25000/- for this academic year 2019-20 too. The 12 months validity period will be from the date of payment made.
</b>
</p>

<p>
<b><u>Account Payable details :</u></b>  (same as for the 1st year payment)
<br>A/C Beneficiary Name: Registrar, IIT Bombay 
<br>A/C Number: 2724101113370 
<br>Bank Name: Canara Bank 
<br>Bank Branch: IIT Powai 
</p>

<p>
<b><u>Important Note</u></b> - If you have already done the payment for the renewal please share the details given with your State Training Manager to track your payment status. OR share the date of making payment for the same to avoid interruption in the training program. If you pay before the expiry date, college will STILL have validity of 12 months from the date of payment. Eg. if validity is there till Oct 2019 and you pay now in Sept 2019, the validity period will still be till Oct 2020.
</p>

<p>
<b><u>Details to be shared by Colleges after making the payment  (Mandate)</u></b>
UTR (Unique Transaction reference), Number of Payer, Name of the payer,Institute name registered for GST, Email ID, Phone number of the Payer, Date of Payment, GST Number, PAN Number.
</p>

<p>
Here's wishing you the best and guaranteeing our continued support for offering the Spoken Tutorial Software training to all. If you have questions, please contact the Training Coordinator of your respective state.
</p>

<p><b>Yours Sincerely, <br>
Shyama Iyer
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
    except Exception as e:
        print(e)
        #print to," => not sent (",count,"/",tot_count,")"
        success_log_file_head.write(str(organiser.user.email)+','+str(0)+'\n')
    #break
print("--------------------------------")
print(tot_count)
print(("Total sent mails:", sent))
print(("Total not sent mails:", notsent))
print("--------------------------------")
