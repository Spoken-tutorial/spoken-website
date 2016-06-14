from models import MdlUser
from events.models import *
from django.core.mail import EmailMultiAlternatives
import hashlib


def encript_password(password):
    password = hashlib.md5(password + 'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()
    return password


def get_moodle_user(academic_id, firstname, lastname, gender, email):
    username = email
    mdluser = None
    try:
        mdluser = MdlUser.objects.filter(email=email).first()
        if not mdluser.institution == academic_id:
            mdluser.institution = academic_id
        if not mdluser.firstname == firstname:
            mdluser.firstname = firstname
        if not mdluser.lastname == lastname:
            mdluser.lastname = lastname
        if not mdluser.gender == gender:
            mdluser.gender = gender
        if not mdluser.username == email:
            mdluser.username = email
        """password = encript_password(firstname)
        if not mdluser.password == password:
            mdluser.password = password"""
        mdluser.save()
    except Exception:
        try:
            mdluser = MdlUser()
            mdluser.auth = 'manual'
            mdluser.firstname = firstname
            mdluser.username = username
            mdluser.lastname = lastname
            mdluser.password = encript_password(firstname)
            mdluser.institution = academic_id
            mdluser.email = email
            mdluser.confirmed = 1
            mdluser.mnethostid = 1
            mdluser.gender = gender
            mdluser.save()
            mdluser = MdlUser.objects.filter(email=email, firstname=firstname,
                                             username=username, password=password).first()

            # send password to email
            subject = "Spoken Tutorial Online Test password"
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
                to=to, bcc=[], cc=[],
                headers={'Reply-To': 'no-replay@spoken-tutorial.org', "Content-type": "text/html;charset=iso-8859-1"}
            )
            email.send(fail_silently=False)

        except:
            return MdlUser.objects.filter(email=email).first()
    return mdluser
