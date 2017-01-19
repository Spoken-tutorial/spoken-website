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

def send_veriy_email(request,email):
  try:
    user = User.objects.get(email = email)
  except ObjectDoesNotExist:
    messages.error(request, "User not registerd in the system")
    return render(request, "cms/templates/verify_email.html")
  
  try:
    student = Student.objects.get(user_id = user.id)
  except ObjectDoesNotExist:
    #not a student so only user
    if not user.is_active :
      #send user activation link mail
      send_registration_confirmation(user)
      messages.success(request, 'Please confirm your verification by clicking on the activation link which has been sent to your registered email id.')
      return render(request, "cms/templates/verify_email.html")
    else:
      messages.success(request, 'User is already activated')
      return render(request, "cms/templates/verify_email.html")
  #is student so proceed with following,
  if student.verified:
    messages.success(request, 'User is already verified')
    return render(request, "cms/templates/verify_email.html")
  else:
    #send email to students 
    #sb = StudentBatch.objects.get(id__in = StudentMaster.objects.filter(student=student).values_list('batch_id'))
    if send_student_mail(email):
      messages.success(request, 'Please check your login details that has been sent to your registered email id')
    else:
      messages.error(request, 'Something went wrong!. Please try again!')
    return render(request, "cms/templates/verify_email.html")
      
def send_student_mail(email):
  mdluser = MdlUser.objects.filter(email=email).first()
  mdl_username = email
  
  password_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
  password_encript = encript_password(password_string)
  mdl_new_password = password_encript
  
  mdluser.password = mdl_new_password
  mdluser.save()
  
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
'''.format(mdluser.firstname, mdluser.username, password_string, "http://spoken-tutorial.org/accounts/confirm_student/" + mdl_new_password + "/" + mdluser.id)

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
