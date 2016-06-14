# Third Party Stuff
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

# Spoken Tutorial Stuff
from events.models import *

plaintext = get_template('email-template.txt')
htmly = get_template('email-template.html')
text_content = plaintext.render()
html_content = htmly.render()

organisers = Organiser.objects.filter(status=1)

sent = 0
notsent = 0
count = 0
tot_count = len(rows)

subject = "Spoken Tutorial Software Training Program"
message = '''Dear Organiser,

<b>Many </b>thanks to you and your Institute for being a part of the Spoken Tutorial Software training program and contributing towards making it such a mega success. This is to inform you that we have introduced a separate interface in the Training Dashboard of our website, namely the Semester Training Planner (STP), that has to be completed prior to raising the Training Request. This ensures that all the batches belonging to the different departments and the specific semesters are able to take training in maximum possible relevant FOSS.The Institute will

    1. Appoint Faculty coordinator/s (FC) - so as to cover maximum departments in the Institute.

    2. As a first step in the Training process, each FC will Register/ Create a login ID

    3. Second step, complete the STP with details -
       Dept. name/s (single/multiple), Semester number (single semester), Semester start date, FOSS Course selection method -
       i)   Mapped with computer lab course hours,
       vii)  Unmapped but during computer lab course hours,
       iii) Outside lab course hours/time-table.
       N.B : Many of you have completed mapping of FOSS courses in your time-tables so this part should not be difficult to do.

    4. Third step, FC will upload a Master Batch (all students in that Dept. and Year), .csv file of Student details -
       i)   Dept. name
       ii)  Year of joining
       iii) First name, Last name, Valid e-mail ID, Gender

    5. Fourth step, complete the Training Request form which is to be filled within 10 weeks of Semester start date in the case of FOSS courses that come with Online Assessment Tests. This is so that students get adequate time to completely revise the entire series of tutorials of the particular FOSS course.

    6. In the fourth step, the FC will select from the Master Batch to create a list with the names of students who will learn the particular FOSS/s

    7. In the fifth step, the FC will need to download the specified software, for that Click below.
       Link : http://process.spoken-tutorial.org/images/1/1b/Download-Tutorials.pdf

       And get the lab and systems ready for the training Click below
       Link : http://process.spoken-tutorial.org/images/5/58/Machine-Readiness.pdf

IMPORTANT - Learner's Certificates will no longer be provided for FOSS courses that come with Online assessment Tests. For these courses, only Completion Certificate will be given on successfully completing and passing the test.

As before, the students must go through the instruction sheet and see the tutorials as directed in the instructions mentioned in it and also practice the commands and instruction as shown in the tutorial following the Side by Side method during the Training. Side by Side means that on the screen, we keep the terminal/console window open on the right hand side for the practice and the tutorial window open on the left hand side for the learning.

Here's wishing you the best and guaranteeing our continued support for offering the Spoken Tutorial Software training to all.

Regards,
Spoken Tutorial Team,
IIT Bombay.'''


for organiser in organisers:
    to = organiser.user.email
    to = ['k.sanmugam2@gmail.com']
    email = EmailMultiAlternatives(
        subject, text_content, 'administrator@spoken-tutorial.org',
        to=to,
        headers={
            "Content-type": "text/html"
        }
    )
    email.attach_alternative(html_content, "text/html")
    count = count + 1
    try:
        result = email.send(fail_silently=False)
        sent += 1
        cur.execute("INSERT INTO organiser_sent_email (user_id) VALUES (" + str(organiser.user.id) + ")")
        if sent % 50 == 0:
            time.sleep(5)
        print to, " => sent (", str(count), "/", str(tot_count), ")"
    except Exception, e:
        print e
        print to, " => not sent (", count, "/", tot_count, ")"
    break
print "--------------------------------"
print "Total sent mails:", sent
print "Total not sent mails:", notsent
print "--------------------------------"
