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
users = InductionFinalList.objects.all()
sent = 0
notsent = 0
count = 0
tot_count = len(users)

subject = '"Instructions for uploading the college letter and paying the registration fee"'

success_log_file_head = open(LOG_ROOT+'induction_particiants_shortlist.txt',"w")
for user in users:
    message = '''
Dear Candidate,

As mentioned in the previous email, you have to upload a scanned copy of the certificate from your Principal/Director/VC, stating that you are in the first two years of service as a teacher.
The format for this certificate is in the attachment.

Instructions to upload the certificate:

Click on this link http://induction.spoken-tutorial.org/mod/assign/view.php?id=1&action=editsubmission
Login using your registered email id.  The password is "student", without quotes.
You will be directed to a page that prompts you to change your password. 

After doing this, you will be taken to a page with the title "Upload college letter".
Drag-and-drop the soft-copy of the college letter, in the space provided.
Click on "Save Changes" button at the bottom of the page.
A confirmation screen will appear.  Click on "Submit assignment" button, which is at the bottom.
A second confirmation screen will appear.  Here click on "Continue" button.
You will see a message "Submitted for grading" in green, in the centre of the page.
Your certificate has now been uploaded.
You may now logout.
You will have to submit the original letter at our Registration Desk on arrival at IIT Bombay.


The second step is to pay the non-refundable course fees of Rs.1,000 through online transfer.
Click on this link http://induction-training-programme.doattend.com
On this page, it will prompt you to type the secret-code/password.  Pls type "pm3nmt2", without quotes, in the textbox provided.
You will be directed to a page that prompts you to purchase tickets.  You have to select 1 ticket from the drop-down box.  Then click on "Register" button.
Now, you will be taken to the Registration page where you have to provide your email id.  Pls type your registered email id in the textbox provided.
Then click on "Continue" button.
It will take you to another page, where you have to 
    1. fill your personal details.  
    2. accept the terms and conditions.
    3. select any one online payment option.
    4. fill your billing details and complete the payment.
Please give the exact same details as given in the "Expression of Interest" form, wherever applicable.

Lastly, click on "Continue" button at the bottom of the page.

Once you complete the payment formalities, you will receive an e-ticket, with a unique ticket number.  
Please take a printout and carry the same with you for submission at our Registration Desk on arrival at IIT Bombay.

The last date to complete the above two activities is now extended to Monday, 13 November 2017, 10 a.m.  After this date, all unfilled seats will be released to people on the waitlist.

Please do not share the above information with anyone else. Candidates who are not selected would not get this mail.  If they still pay using the above information, they will not get a refund, nor will they be admitted to the Training Programme.

Look forward to meeting you.

Best Wishes,
Prof Kannan Moudgalya
PI, PMMMNMTT
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
