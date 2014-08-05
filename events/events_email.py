from django.core.mail import EmailMultiAlternatives

def send_email(status, to = None, instance = None, cc = None, bcc = None):
    # Sending email when an answer is posted
    #status = 'No training request 15 days after registered as Organiser'
    subject = None
    if status == 'Fix a date for your first training':
        subject  = 'Important : Fix a date for your first workshop'
        message = '''Dear Organiser,
        
        You have registered into the spoken-tutorial.org website over 2 weeks back. Please fix a date and time and make a training request if you want to organise training workshops. Click on the link below for the instructions to request the workshop: {0}

        If you have any questions, call or write to your Spoken Tutorial IIT Bombay, team person whose contact details you have. See the link for the contact details of person incharge for your state {1}

Regards,
Spoken Tutorial
'''.format('http://process.spoken-tutorial.org/images/8/89/Workshop-Request-Sheet.pdf', 'http://process.spoken-tutorial.org/index.php/Software-Training#Contacts_For_Workshops')

    elif status == 'Instructions to be followed before conducting the training':
        subject  = 'Important :  Post approved training request'
        message = '''Dear Organiser,
        
Your training on {2}, requested on {3} {4} has been approved. Please find the
workshop code. {5}. This code is very important, please preserve it for your future reference.

If you have clicked YES for Skype support then you can send us a request on our Skype ID namely st-wshop
and st-iitb. Any day before the training please call us on Skype to have a Skype testing session and
interact with Spoken Tutorial, IIT Bombay team.

You also need to download the specified software, for that Click below.
{0}

For getting the lab and systems ready for the training Click below
{1}

Regards,
Spoken Tutorial
'''.format('http://process.spoken-tutorial.org/images/1/1b/Download-Tutorials.pdf', 'http://process.spoken-tutorial.org/images/5/58/Machine-Readiness.pdf', instance.foss, instance.trdate, instance.trtime, instance.training_code)
    
    elif status == 'How to upload the attendance on the training day':
        subject  = 'Important : How to upload the attendance on the training day.'
        
        message = '''Dear Organiser,
        
You have the training {1} on {2} at your Institute. Kindly upload the attendance list of students
who will participate in the workshop, on the training day. To do that Login on {0}
website, Click on Upload attendance and upload the xml file you have created in your system. This
activity has to be done before you organise more workshops or make the test request.

Please ensure that the students do go through the instruction sheet and see the tutorials as directed in the
instructions mentioned in it and also practice the commands and instruction as shown in the tutorial following
the Side by Side method during the workshop.

Side by Side means that on the screen, we keep the terminal/console window open on the right hand side for
the practise and the tutorial window open on the left hand side for the learning.

Regards,
Spoken Tutorial
'''.format('http://spoken-tutorial.org', instance.training_code, instance.foss)
    
    elif status == 'Future activities after conducting the workshop':
        subject  = 'Important : Future activities after conducting the workshop.'
        message = '''Dear Organiser,
        
You have successfully completed the training {3} on {4} at your institute. Please see the
following instructions for the future activities.

Bulk Workshops

It is necessary for all students in the Institute to get the opportunity to take Spoken Tutorial based software
training. For this please spread the awareness about the workshops in other departments amongst the
Faculty. You can also request the Principal to send out a circular to all. For your department prepare a
calendar/time-table to organise workshops for all the student batches in a systematic way. Send us the
confirmed schedule soon for the upcoming workshops. To view sample calenders Click here. To know which software is relevant for which department Click here

Online Assessment test

After the workshop, the participants need to complete listening to all the tutorials and practice well including
solving the assignment questions. This revision needs to be done at least 2 times so that the students are
ready to take the online test. The organiser needs to keep a watch that proper revision is being done. Total
time taken can be anywhere from 2 weeks to 1 month or even more. Fix the online test date after
confirming that all students have practiced well.

Please note that an invigilator is required for the online test. For this, identify a faculty member who can
invigilate the test and help him/her register on the {0} website before you make a test request.
Click on the link below for the instructions for invigilator:
{1}

To make an online Test Request please Click here.
{2} for the instructions on how to request the test

Regards,
Spoken Tutorial
'''.format('http://spoken-tutorial.org', 'process.spoken-tutorial.org/images/0/09/Instructions_for_Invigilator.pdf','http://process.spoken-tutorial.org/images/a/aa/Test_Request.pdf', instance.training_code, instance.foss )

    elif status == 'Instructions to be followed before conducting the test-organiser':
        subject  = 'Important : Instructions to be followed before conducting the test.'
        message = '''Dear Organiser,
        
Your {2} test on {3} {4} has been approved. The test code is {5}. This code is
very important, please preserve it for your future reference and also share it with the students and invigilator
on the test day. The link for the online test is {0}

Inform all the participants to get the scan copy of their photographs on the test day. Get well versed with the
online test before the test, see the link below for the instructions of online test for the participants
{1}

All the Best to you and all the participants.

Regards,
Spoken Tutorial
'''.format('http://onlinetest.spoken-tutorial.org/', 'http://process.spoken-tutorial.org/images/9/95/Test_Instruction_for_Participants.pdf', instance.foss, instance.tdate, instance.ttime, instance.test_code)

    elif status == 'Instructions to be followed before conducting the test-invigilator':
        subject  = 'Important : Instructions to be followed before conducting the test.'
        message = '''Dear Invigilator,
        
The organiser has requested for the {1} test on {2} {3}. Please confirm your
presence by logging in our website with your username and password and Click on confirmation for the
Assessment test.

Please go through the instructions below to know what to do on the test day. Click on the link below.
{0}
Do not forget to Close the test after the completion of the test.


Regards,
Spoken Tutorial
'''.format('http://process.spoken-tutorial.org/images/0/09/Instructions_for_Invigilator.pdf', instance.foss, instance.tdate, instance.ttime, instance.test_code)

    elif status == "Learner's Certificate":
        subject  = "Learner's Certificate"
        message = '''The Gold Certificate will be generated on the basis of the test but many of our series do not have test so
please upload the attendance within 48 hrs after the training so that the students can get the Silver /
Learner's certificate

Regards,
Spoken Tutorial
'''.format()

    # send email
    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
        to = to, bcc = bcc, cc = cc,
        headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
    )
    
    #print "*******************************************************"
    #print message
    #print "*******************************************************"
    #email.attach_alternative(message, "text/html")
    try:
        result = email.send(fail_silently=False)
    except Exception, e:
        pass
