from django.shortcuts import render
from cms.models import *
from events.models import Student, StudentBatch
from mdldjango.models import MdlUser
from django.contrib import messages
from mdldjango.get_or_create_participant import get_or_create_participant, encript_password
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
import smtplib
import hashlib
import random
import string
from hashids import Hashids

def get_user_email(email):
  try:
    user = User.objects.filter(email__iexact=email)
    if len(user) == 1:
      return user[0]
    return User.objects.get(email=email).first()
  except ObjectDoesNotExist:
    return None

def send_user_registration_confirmation(user):
    p = Profile.objects.get(user=user)
    #user.email = "k.sanmugam2@gmail.com"
    # Sending email when an answer is posted
    subject = 'Account Active Notification'
    message = """Dear {0},

Thank you for registering at {1}. You may activate your account by clicking on this link or copying and pasting it in your browser
{2}

Regards,
Admin
Spoken Tutorials
IIT Bombay.
    """.format(
        user.username,
        "http://spoken-tutorial.org",
        "http://spoken-tutorial.org/accounts/confirm/" + str(p.confirmation_code) + "/" + user.username
    )

    email = EmailMultiAlternatives(
        subject, message, 'no-reply@spoken-tutorial.org',
        to = [user.email], bcc = [], cc = [],
        headers={'Reply-To': 'no-reply@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
    )

    #email.attach_alternative(message, "text/html")
    try:
      result = email.send(fail_silently=False)
      return True
    except smtplib.SMTPException:
      print "Failed to send email to user"
      return False

def send_verify_email(request,email):
  message = None
  user_login = "http://spoken-tutorial.org/accounts/login/"
  student_login = "http://spoken-tutorial.org/participant/login/"
  user = get_user_email(email)
  if not user:
    message = "User "+email+" not registerd in the system."
    return False, message
  try:
    student = Student.objects.get(user_id = user)
  except ObjectDoesNotExist:
    #not a student so only user
    if not user.is_active :
      #send user activation link mail
      user_mail_status = send_user_registration_confirmation(user)
      if user_mail_status:
        message = 'Please confirm your verification by clicking on the activation link which has been sent to your registered email id '+email+'.'
        return True, message
      else:
        message = 'Something went wrong!. Please try again later!'
        #notify to admin via mail
        return False, message  
    else:
      message = 'User '+email+' is already activated. Kindly visit <a href = '+user_login+' >login</a> page to continue.'
      return True, message
  #is student so proceed with following,
  if student.verified and user.is_active:
    message = 'Participant '+email+' is already verified. Kindly visit <a href = '+student_login+' >login</a> page to continue.'
    return True, message
  else:
    #send email to students
    student_mail_status = send_student_mail(email)
    if student_mail_status:
      message = 'Please check your login details that has been sent to your registered email id.'
      return True, message
    else:
      message = 'Something went wrong!. Please try again later!'
      #notify to admin via mail
      return False, message
      
def send_student_mail(email):
  mdluser = MdlUser.objects.filter(email=email).first()
  mdl_username = email
  
  password_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
  mdl_new_password = encript_password(password_string)
  
  mdluser.password = mdl_new_password
  mdluser.save()
  
  token = Hashids(salt = settings.SPOKEN_HASH_SALT).encode(mdluser.id)
  
  #send mail to student_mail
  subject = "Spoken Tutorial Online Test password"
  to = [mdluser.email]
  message = '''Hi {0},
Your account password at 'Spoken Tutorials Online Test as follows'

Your current login information is now:
username: {1}
password: {2}

Please click below link to activate your account:
{3}

In most mail programs, this should appear as a blue link
which you can just click on.  If that doesn't work,
then cut and paste the address into the address
line at the top of your web browser window.

Cheers from the 'Spoken Tutorials Online Test Center' administrator,

Admin Spoken Tutorials
'''.format(mdluser.firstname, mdluser.username, password_string, "http://spoken-tutorial.org/accounts/confirm_student/" + token)

  # send email
  email = EmailMultiAlternatives(
    subject, message, 'administrator@spoken-tutorial.org',
    to=to, bcc=[], cc=[],
    headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type": "text/html;charset=iso-8859-1"}
  )
  try:
    result = email.send(fail_silently=False)
    return True
  except smtplib.SMTPException:
    print "Failed to send email"
    return False
