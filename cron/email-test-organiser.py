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

subject = '"Method to select 120 participants for the Induction Training Programme"'

success_log_file_head = open(LOG_ROOT+'induction_particiants.txt',"w")
for user in users:
    message = '''
Hello,

Thank you for your interest in participating in the Induction Training Programme, organised under the aegis of the Pandit Madan Mohan Malaviya National Mission on Teachers and Teaching.  You have made it to the first shortlist.  We invite you to offer yourself to be selected in the top 120 people. 

Shortlisting from amongst the teachers, for a training programme, is a tricky one.  It may not make sense to select on the basis of marks one scored in a qualifying degree, for example.  Selection based on metric, such as perseverance, motivating others, teaching others through personal examples, etc., would make a lot more sense.  This is precisely what the Knack promises to do!  Developed by Dr. Guy Halftec, the Knack helps identify the level of skills/talents, etc., of the player of a game, called a knack.  We hope to use these scores to shortlist people for the next stage.

Please follow this link on your phone to download and play the games - knack.it/bbddmm.  Sign up and login using the same e-mail address that you shared with us - if you use some other email address, you may NOT be shortlisted.  Please enter xepw as the Knack Code (optional), when prompted.  Please do exactly as suggested above.  Attached are the screenshots for your convenience. 

Please ensure that you have about 45 minutes of time, your phone is fully charged, etc., before starting to play.  Scores obtained from the first time of play only will be considered.  You may play again, but those scores will NOT be considered.  This is how the game engine is built, and it cannot be changed for any reason.

As soon as you complete playing, we shall automatically get your score from the Knack game.  Please complete this activity before the due date of 3 November 2017, 5pm.

Thanks and regards,
Prof. Kannan Moudgalya
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
    email.attach_file('/websites_dir/django_spoken/spoken/cron/Knack-user-flow.pdf')
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

