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
users = User.objects.filter(is_active = 1)
sent = 0
notsent = 0
count = 0
tot_count = len(users)

subject = '"HT for Mumbai" Award: Please vote for Prof. Kannan Moudgalya.'

success_log_file_head = open(LOG_ROOT+'happy-new-year-reminder-notify.txt',"w")
for user in users:
    message = '''

Greetings from the Spoken Tutorial Project, IIT Bombay.

Prof Kannan Moudgalya, who leads the efforts of the Spoken Tutorial Project, has been nominated for the Hindustan Times "HT for Mumbai awards" 2015.

From his profile that appeared in Hindustan Times (http://spoken-tutorial.org/media/news/772/772.pdf), you will see that this is a recognition of our IT literacy campaign through Spoken Tutorials.

Pls visit this link and vote for him under the individual nominees category. His victory is the Project's victory.
http://spoken-tutorial.org/ht-for-mumbai-nomination/


Spread the word and help him and our Project win! 

Last date for voting is 9 Jan 2016.

Thank you in advance.

--
Regards,
Spoken Tutorial Team,
IIT Bombay.'''.format(user.username)

    to  = [user.email]
    #to = ['k.sanmugam2@gmail.com']
    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
        to = to,
        headers = {
         "Content-type" : "text/html"
        }
    )
    #email.attach_alternative(html_content, "text/html")
    count = count + 1
    try:
        result = email.send(fail_silently=False)
        sent += 1
        # cur.execute("INSERT INTO organiser_sent_email (user_id) VALUES (" + str(user.id) + ")")
        if sent%100 == 0:
            time.sleep(10)
        #print to," => sent (", str(count),"/",str(tot_count),")"
        success_log_file_head.write(str(user.id)+','+str(1)+'\n')
    except Exception, e:
        print e
        #print to," => not sent (",count,"/",tot_count,")"
        success_log_file_head.write(str(user.id)+','+str(0)+'\n')
    #break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"
