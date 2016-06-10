from django.core.mail import EmailMultiAlternatives


def send_email(status, to=None, instance=None, cc=None, bcc=None):
    subject = None
    # Mail 1
    if status == 'Fix a date for your first training':
        subject = 'Important : Fix a date for your first Training'
        message = '''Dear Organiser,

        You have registered into the {2} website over 2 weeks back. Please arrange a batch of students, fix a date and time and make a training request in order to organise Trainings. Click on the link below for the instructions to request the Training: {0}

        If you have any questions, call or write to your Spoken Tutorial IIT Bombay, team person whose contact details you have. See the link for the contact details of person in-charge for your state {1}

        Note: PLEASE ENSURE THAT YOU FILL IN ONLY THE GENUINE EMAIL ID'S OF THE PARTICIPANTS / STUDENTS. IF THEY DON'T HAVE ANY, PLEASE HELP THEM CREATE ONE

Regards,
Spoken Tutorial Team,
IIT Bombay.
'''.format('http://process.spoken-tutorial.org/images/1/1f/Training-Request-Sheet.pdf', 'http://process.spoken-tutorial.org/index.php/Software-Training#Contacts_For_Training', 'http://spoken-tutorial.org')

    # Mail 2
    elif status == 'Instructions to be followed before conducting the training':
        subject = 'Important : Instructions to be followed before conducting the training'
        message = '''Dear Organiser,

Thank you for making the Training request on {0} to be conducted at your Institute on {1}. The Training Manager at Spoken Tutorial Project Team, IIT Bombay will approve your request shortly.

Please ensure that the students go through the instruction sheet and see the tutorials as directed in the instructions mentioned in it and also practice the commands and instruction as shown in the tutorial following the Side by Side method during the Training.

Side by Side means that on the screen, we keep the terminal/console window open on the right hand side for the practice and the tutorial window open on the left hand side for the learning.

If you have clicked YES for Skype support then you can send us a request on our Skype ID namely st-wshop and st-iitb. Any day before the Training please call us on Skype to have a Skype testing session and interact with Spoken Tutorial, IIT Bombay team.

You also need to download the specified software, for that Click below.
{2}

For getting the lab and systems ready for the workshop Click below
{3}

Regards,
Spoken Tutorial Team,
IIT Bombay.
'''.format(instance.foss, instance.tdate, 'http://process.spoken-tutorial.org/images/c/c2/Participant_data.pdf', 'http://process.spoken-tutorial.org/images/1/1b/Download-Tutorials.pdf', 'http://process.spoken-tutorial.org/images/5/58/Machine-Readiness.pdf', instance.ttime, instance.training_code)

    # Mail 3
    elif status == 'Future activities after conducting the Training':
        subject = 'Important : Future activities after conducting the Training'
        message = '''Dear Organiser,

 You have successfully completed the Training {3} on {4} at your institute. Please see the following instructions for the future activities.

Bulk Trainings

It is necessary for all students in the Institute to get the opportunity to take Spoken Tutorial based software training. For this please spread the awareness about the Trainings in other departments amongst the Faculty. You can also request the Principal to send out a circular to all. For your department prepare a calendar/time-table to organise Trainings for all the student batches in a systematic way. Send us the confirmed schedule soon for the upcoming Trainings. To view sample calenders Click here. To know which software is relevant for which department Click here

Online Assessment test

After the Training, the participants need to complete listening to all the tutorials and practice well including solving the assignment questions. This revision needs to be done at least 2 times so that the students are ready to take the online test. The organiser needs to keep a watch that proper revision is being done. Total time taken can be anywhere from 2 weeks to 1 month or even more. Fix the online test date after confirming that all students have practiced well.


Please note that an invigilator is required for the online test. For this, identify a faculty member who can invigilate the test and help him/her register on the {0} website before you make a test request.

Click on the link below for the instructions for invigilator:
{1}

To make an online Test Request please Click here.
{2} for the instructions on how to request the test

Regards,
Spoken Tutorial Team,
IIT Bombay.
'''.format('http://spoken-tutorial.org', 'process.spoken-tutorial.org/images/0/09/Instructions_for_Invigilator.pdf', 'http://process.spoken-tutorial.org/images/a/aa/Test_Request.pdf', instance.training_code, instance.foss)

    # Email 4
    elif status == 'Instructions to be followed before conducting the test-organiser':
        subject = 'Important : Instructions to be followed before conducting the test - Organiser'
        message = '''Dear Organiser,

Your {1} test on {2} {3} has been approved. The test code is {4}. This code is very important, please preserve it for your future reference and also share it with the students and invigilator on the test day.

Inform all the participants to get the scan copy of their photographs on the test day. Get well versed with the online test before the test, see the link below for the instructions of online test for the participants {0}

All the Best to you and all the participants.

Regards,
Spoken Tutorial Team,
IIT Bombay.
'''.format('http://process.spoken-tutorial.org/images/9/95/Test_Instruction_for_Participants.pdf', instance.foss, instance.tdate, instance.ttime, instance.test_code)

    # Email 5
    elif status == 'Instructions to be followed before conducting the test-invigilator':
        subject = 'Important : Instructions to be followed before conducting the test - Invigilator'
        message = '''Dear Invigilator,

The organiser has requested for the {1} test on {2} {3}. Please confirm your presence by logging in our website with your username and password and Click on confirmation for the Assessment test.

Please go through the instructions below to know what to do on the test day. Click on the link below.
{0}

Do not forget to Close the test after the completion of the test.

Regards,
Spoken Tutorial Team,
IIT Bombay.
'''.format('http://process.spoken-tutorial.org/images/0/09/Instructions_for_Invigilator.pdf', instance.foss, instance.tdate, instance.ttime, instance.test_code)

    # send email
    email = EmailMultiAlternatives(
        subject, message, 'no-reply@spoken-tutorial.org',
        to=to, bcc=bcc, cc=cc,
        headers={
            'Reply-To': 'no-reply@spoken-tutorial.org',
            "Content-type": "text/html;charset=iso-8859-1"
        }
    )

    try:
        email.send(fail_silently=True)
    except Exception:
        print "*******************************************************"
        print message
        print "*******************************************************"
        pass
