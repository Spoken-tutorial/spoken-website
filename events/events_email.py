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
'''.format('http://process.spoken-tutorial.org/images/1/1f/Training-Request-Sheet.pdf', 'http://process.spoken-tutorial.org/index.php/Software-Training#Contacts_For_Training')

    elif status == 'Instructions to be followed before conducting the training':
        subject  = 'Important : Instructions to be followed before conducting the training'
        message = '''Dear Organiser,
        
Thank you for making the Training / workshop request on {3} to be conducted at your Institute. Please upload the "Participant List" of students who are expected to take part in the Training BEFORE the Training / Workshop. The Training Manager at Spoken Tutorial Project Team, IIT Bombay will only be able to approve your request if "Participant List" is Uploaded.

Please click on the following link to know the Instructions to upload the Participant Details :

{0}

Note: It is necessary that you upload the "Participant List" while you raise the Training / Workshop Request, for the Training Manager to approve your request.

As soon as the Training Manager approves, you will get the Training / Workshop code {6}. This code is very important, please preserve it for your future reference.

Please ensure that the students go through the instruction sheet and see the tutorials as directed in the instructions mentioned in it and also practice the commands and instruction as shown in the tutorial following the Side by Side method during the Training / workshop.

Side by Side means that on the screen, we keep the terminal/console window open on the right hand side for the practice and the tutorial window open on the left hand side for the learning.

If you have clicked YES for Skype support then you can send us a request on our Skype ID namely st-wshop and st-iitb. Any day before the Training / workshop please call us on Skype to have a Skype testing session and interact with Spoken Tutorial, IIT Bombay team.

You also need to download the specified software, for that Click below.
{1}

For getting the lab and systems ready for the workshop Click below
{2}

Regards,
Spoken Tutorial
'''.format('http://process.spoken-tutorial.org/images/c/c2/Participant_data.pdf', 'http://process.spoken-tutorial.org/images/1/1b/Download-Tutorials.pdf', 'http://process.spoken-tutorial.org/images/5/58/Machine-Readiness.pdf', instance.foss, instance.trdate, instance.trtime, instance.training_code)
    
    elif status == 'How to upload the attendance on the Workshop day':
        subject  = 'Important : How to upload the attendance on the workshop day'
        
        message = '''Dear Organiser,
        
You have successfully completed the Workshop {0} on {1} at your institute. Please see the following instructions for the future activities.

Recording Attendance

Please record (submit) your attendance by marking on the 'Participant List' which you have uploaded while making the Workshop Request. To know more, click here http://process.spoken-tutorial.org/images/5/5d/Recording_the_attendance_workshop.pdf

N.B.: Only after you submit the 'Participant List' with attendance marked, the participants can download the Learner's Certificate.

Bulk Training / Workshops

Before starting the new semester we can do some planning so that we can start the training in the college in a phased manner. If you have already prepared a Bulk workshop calendar in line with your lab hours or curriculum please share it with me.

The following is the link which will navigate directly to the Sample Calendar page of our Wiki. See some samples from other colleges.
http://process.spoken-tutorial.org/index.php/Software-Training#Sample_Calendar

    1. You need not arrange regular workshops for the softwares which are part of your lab course (C,C++, Java etc.) instead you can introduce Spoken Tutorials on these software courses to students directly during their respective lab hours.
       
    2. Ensure that the Spoken Tutorials are loaded into the systems in the labs in advance. This will make the learning very smooth.
       
    3. This will get off the responsibility and worry about lab availability and structured workshop timings.
       
Kindly go through the link to understand the lab deployment process.

http://process.spoken-tutorial.org/images/7/72/Matching_spoken-tutorial.pdf

For other Software courses which are not part of the lab you can continue the workshop method.

Online Assessment test

After the workshop, the participants need to complete listening to all the tutorials and practise well including solving the assignment questions. This revision needs to be done at least 2 times so that the students are ready to take the online test. The organiser needs to keep a watch that proper revision is being done. Total time taken can be anywhere from 2 weeks to 1 month or even more.

Fix the online test date after confirming that all students have practised well.

N.B.: If you have conducted a software Training session and made the course contents available to the students during the regular lab hours throughout the semester where it matches with the curriculum, then you can schedule the test during or before the end of the semester as per your convenience.

Please note that an invigilator is required for the online test. For this, identify a faculty member who can invigilate the test and help him/her register on the spoken-tutorial.org website before you make a test request.

Click on the link below for the instructions for invigilator:
process.spoken-tutorial.org/images/0/09/Instructions_for_Invigilator.pdf

To make an online Test Request please Click here.
process.spoken-tutorial.org/images/a/aa/Test_Request.pdf for the instructions on how to request the
test.


Regards,
Spoken Tutorial
'''.format(instance.training_code, instance.foss)

    elif status == 'How to upload the attendance on the Training day':
        subject  = 'Important : Instruction to fill the Training Completion Form'
        
        message = '''Dear Organiser,
        
You have successfully completed the Training / Workshop {0} on {1} at your institute. Please see the following instructions for the future activities.

Fill up Training Completion Form

Please complete the required details in the 'Training Completion Form' for the Training {0} on {1} which you have started on {2} and click on the 'Submit' button. To know more, click here http://process.spoken-tutorial.org/images/0/04/Instruction_Training_completion_form.pdf

N.B.: Only after you fill and submit the 'Training Completion Form', the participants can download the Learner's Certificate.

Bulk Training / Workshops

Before starting the new semester we can do some planning so that we can start the training in the college in a phased manner. If you have already prepared a Bulk workshop calendar in line with your lab hours or curriculum please share it with me.

The following is the link which will navigate directly to the Sample Calendar page of our Wiki. See some samples from other colleges.
http://process.spoken-tutorial.org/index.php/Software-Training#Sample_Calendar

    1. You need not arrange regular workshops for the softwares which are part of your lab course (C,C++, Java etc.) instead you can introduce Spoken Tutorials on these software courses to students directly during their respective lab hours.
    
    2. Ensure that the Spoken Tutorials are loaded into the systems in the labs in advance. This will make the learning very smooth.
    
    3. This will get off the responsibility and worry about lab availability and structured workshop timings.
    
    4. Ensure that the Spoken Tutorials are loaded into the systems in the labs in advance. This will make the learning very smooth.
    
    5. This will get off the responsibility and worry about lab availability and structured workshop timingsself.
       
Kindly go through the link to understand the lab deployment process.

http://process.spoken-tutorial.org/images/7/72/Matching_spoken-tutorial.pdf

For other Software courses which are not part of the lab you can continue the workshop method used in the last academic semester.

Bulk Training / Workshops

Before starting the new semester we can do some planning so that we can start the training in the college in a phased manner. If you have already prepared a Bulk workshop calendar in line with your lab hours or curriculum please share it with me.

The following is the link which will navigate directly to the Sample Calendar page of our Wiki. See some samples from other colleges.
http://process.spoken-tutorial.org/index.php/Software-Training#Sample_Calendar

    1. You need not arrange regular workshops for the softwares which are part of your lab course (C,C++, Java etc.) instead you can introduce Spoken Tutorials on these software courses to students directly during their respective lab hours.
    
    2. Ensure that the Spoken Tutorials are loaded into the systems in the labs in advance. This will make the learning very smooth.
    
    3. This will get off the responsibility and worry about lab availability and structured workshop timingsselfself. Kindly go through the link to understand the lab deployment process.

http://process.spoken-tutorial.org/images/7/72/Matching_spoken-tutorial.pdf

For other Software courses which are not part of the lab you can continue the workshop method used in the last academic semester.

Online Assessment test

After the workshop, the participants need to complete listening to all the tutorials and practice well including solving the assignment questions. This revision needs to be done at least 2 times so that the students are ready to take the online test. The organiser needs to keep a watch that proper revision is being done. Total time taken can be anywhere from 2 weeks to 1 month or even more.

Fix the online test date after confirming that all students have practised well.

N.B.: If you have conducted a software Training session and made the course contents available to the students during the regular lab hours throughout the semester where it matches with the curriculum, then you can schedule the test during or before the end of the semester as per your convenience.

Please note that an invigilator is required for the online test. For this, identify a faculty member who can invigilate the test and help him/her register on the spoken-tutorial.org website before you make a test request.

Click on the link below for the instructions for invigilator:

process.spoken-tutorial.org/images/0/09/Instructions_for_Invigilator.pdf
To make an online Test Request please Click here.

process.spoken-tutorial.org/images/a/aa/Test_Request.pdf for the instructions on how to request the test.


Regards,
Spoken Tutorial
'''.format(instance.training_code, instance.foss, instance.trdate)

    
    elif status == 'Future activities after conducting the workshop':
        subject  = 'Important : Future activities after conducting the workshop'
        message = '''Dear Organiser,
        
You have successfully completed the training {3} on {4} at your institute. Please see the following instructions for the future activities.

Bulk Workshops

It is necessary for all students in the Institute to get the opportunity to take Spoken Tutorial based software training. For this please spread the awareness about the workshops in other departments amongst the Faculty. You can also request the Principal to send out a circular to all. For your department prepare a calendar/time-table to organise workshops for all the student batches in a systematic way. Send us the confirmed schedule soon for the upcoming workshops. To view sample calenders Click here. To know which software is relevant for which department Click here

Online Assessment test

After the workshop, the participants need to complete listening to all the tutorials and practice well including solving the assignment questions. This revision needs to be done at least 2 times so that the students are ready to take the online test. The organiser needs to keep a watch that proper revision is being done. Total time taken can be anywhere from 2 weeks to 1 month or even more. Fix the online test date after confirming that all students have practiced well.

Please note that an invigilator is required for the online test. For this, identify a faculty member who can invigilate the test and help him/her register on the {0} website before you make a test request.

Click on the link below for the instructions for invigilator:
{1}

To make an online Test Request please Click here.
{2} for the instructions on how to request the test

Regards,
Spoken Tutorial
'''.format('http://spoken-tutorial.org', 'process.spoken-tutorial.org/images/0/09/Instructions_for_Invigilator.pdf','http://process.spoken-tutorial.org/images/a/aa/Test_Request.pdf', instance.training_code, instance.foss )

    elif status == 'Instructions to be followed before conducting the test-organiser':
        subject  = 'Important : Instructions to be followed before conducting the test - Organiser'
        message = '''Dear Organiser,
        
Your {2} test on {3} {4} has been approved. The test code is {5}. This code is very important, please preserve it for your future reference and also share it with the students and invigilator on the test day. The link for the online test is {0}

Inform all the participants to get the scan copy of their photographs on the test day. Get well versed with the online test before the test, see the link below for the instructions of online test for the participants {1}

All the Best to you and all the participants.

Regards,
Spoken Tutorial
'''.format('http://onlinetest.spoken-tutorial.org/', 'http://process.spoken-tutorial.org/images/9/95/Test_Instruction_for_Participants.pdf', instance.foss, instance.tdate, instance.ttime, instance.test_code)

    elif status == 'Instructions to be followed before conducting the test-invigilator':
        subject  = 'Important : Instructions to be followed before conducting the test - Invigilator'
        message = '''Dear Invigilator,
        
The organiser has requested for the {1} test on {2} {3}. Please confirm your presence by logging in our website with your username and password and Click on confirmation for the Assessment test.

Please go through the instructions below to know what to do on the test day. Click on the link below.
{0}

Do not forget to Close the test after the completion of the test.


Regards,
Spoken Tutorial
'''.format('http://process.spoken-tutorial.org/images/0/09/Instructions_for_Invigilator.pdf', instance.foss, instance.tdate, instance.ttime, instance.test_code)

    elif status == "Learner's Certificate":
        subject  = "Learner's Certificate"
        message = '''The Gold Certificate will be generated on the basis of the test but many of our series do not have test so
please upload the attendance within 48 hrs after the training so that the students can get the Silver / Learner's certificate

Regards,
Spoken Tutorial
'''.format()

    # send email
    email = EmailMultiAlternatives(
        subject, message, 'administrator@spoken-tutorial.org',
        to = to, bcc = bcc, cc = cc,
        headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
    )
    
    try:
        result = email.send(fail_silently=False)
    except Exception, e:
        print "*******************************************************"
        print message
        print "*******************************************************"
        pass
