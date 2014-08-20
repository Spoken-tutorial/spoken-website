import random, string, hashlib
from models import MdlUser
from events.models import TrainingAttendance
from django.core.mail import EmailMultiAlternatives

def encript_password(password):
    password = hashlib.md5(password+'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()
    return password
    
def get_or_create_participant(w, firstname, lastname, gender, email, category):
    password_string = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    password_encript = encript_password(password_string)

    password = password_encript
    username = email
    try:
        mdluser = MdlUser.objects.filter(email = email).first()
        mdluser.institution = w.academic_id
        mdluser.firstname = firstname
        mdluser.lastname = lastname
        mdluser.gender = gender
        mdluser.save()
    except Exception, e:
        mdluser = MdlUser()
        mdluser.auth = 'manual'
        mdluser.firstname = firstname
        mdluser.username = username
        mdluser.lastname = lastname
        mdluser.password = password
        mdluser.institution = w.academic_id
        mdluser.email = email.lower()
        mdluser.confirmed = 1
        mdluser.mnethostid = 1
        mdluser.gender = gender
        mdluser.save()
        mdluser = MdlUser.objects.filter(email = email, firstname= firstname, username=username, password=password).first()
        
        # send password to email
        subject  = "Spoken Tutorial Online Test password"
        to = [mdluser.email]
        message = '''Hi {0},

Your account password at 'Spoken Tutorials Online Test as follows'

Your current login information is now:
username: {1}
password: {2}

Please go to this page to change your password:
{3}

In most mail programs, this should appear as a blue link
which you can just click on.  If that doesn't work,
then cut and paste the address into the address
line at the top of your web browser window.

Cheers from the 'Spoken Tutorials Online Test Center' administrator,

Admin Spoken Tutorials
'''.format(mdluser.firstname, mdluser.username, password_string, 'http://onlinetest.spoken-tutorial.org/login/change_password.php')

        # send email
        email = EmailMultiAlternatives(
            subject, message, 'administrator@spoken-tutorial.org',
            to = to, bcc = [], cc = [],
            headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
        )

        result = email.send(fail_silently=False)
        #print "-----------------------------------------"
        #print message
        #print "-----------------------------------------"
    if category == 2:
        try:
            wa = TrainingAttendance.objects.get(training_id = w.id, mdluser_id = mdluser.id)
        except Exception, e:
            #print e
            wa = TrainingAttendance()
            wa.training_id = w.id
            wa.status = 1
            wa.mdluser_id = mdluser.id
            wa.save()
