from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from mdldjango.models import MdlUser

from hashlib import md5
from string import digits, ascii_uppercase
from random import sample


class Command(BaseCommand):
    help = 'Migrates user from django to moodle.\n\
            Send user credentials via email.'
    FROM = 'administrator@spoken-tutorial.org'
    SUBJECT  = "Spoken Tutorial Online Test password"
    HEADERS = {'Reply-To': 'no-replay@spoken-tutorial.org',
            "Content-type":"text/html;charset=iso-8859-1"}

    def handle(self, *args, **options):
        users = self.get_spoken_user()
        self.log(users.count())

        for user in users:
            if self.is_student(user):
                self.log(user)
                if not self. is_moodle_user(user):
                    self.log(user.email+" not in moodle")
                    academy = self.get_academy(user)
                    if academy:
                        self.log(academy)
                        password = self.get_raw_password()
                        mdluser = self.add_moodle_user(user, password, academy)
                        if mdluser:
                            self.log("Added to moodle")
                            ex, res = self.send_email(mdluser, password)
                            self.log(ex)
                            self.log('+')
                            self.log(res)
                        else:
                            self.log("user not added")
                    else:
                        self.log("no academy")
                else:
                    self.log(user.email+" in moodle")
            else:
                self.log(user)
                self.log("not student")


    def get_spoken_user(self):
        return User.objects.all()


    def is_student(self, user):
        try:
            if user.student:
                return True
        except Exception:
            return False


    def is_moodle_user(self, user):
        try:
            if MdlUser.objects.get(email=user.email):
                return True
        except MdlUser.DoesNotExist:
            return False
        except MdlUser.MultipleObjectsReturned:
            return True


    def get_academy(self, user):
        try:
            return user.student.studentmaster_set.all().first().batch.organiser.academic
        except AttributeError:
            return None


    def add_moodle_user(self, user, password, academy):
        ''' Creates moodle account and sends email'''
        mdluser = MdlUser()
        mdluser.auth = 'manual'
        mdluser.firstname = user.first_name
        mdluser.lastname = user.last_name
        mdluser.username = user.email
        mdluser.password = self.encrypt_password(password)
        mdluser.institution = academy
        mdluser.gender = user.student.gender
        mdluser.email = user.email
        mdluser.confirmed = 1
        mdluser.mnethostid = 1
        mdluser.save()
        return mdluser


    def get_raw_password(self):
        return  ''.join(sample(ascii_uppercase + digits, 8))


    def encrypt_password(self, password):
        return md5(password+'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()


    def send_email(self, user, password):
        result = None
        message = '''Hi {0},

Your account password at 'Spoken Tutorials Online Test as follows'

Your current login information is now:
username: {1}
password: {2}

Please go to this page to change your password:
http://onlinetest.spoken-tutorial.org/login/change_password.php

In most mail programs, this should appear as a blue link
which you can just click on.  If that doesn't work,
then cut and paste the address into the address
line at the top of your web browser window.

Cheers from the 'Spoken Tutorials Online Test Center' administrator,

Admin Spoken Tutorials
'''
        message = message.format(user.firstname, user.username, password)
        self.log(message)
        email = EmailMultiAlternatives(self.SUBJECT, message, self.FROM,
            to = [user.email], bcc = [], cc = [], headers=self.HEADERS)
        self.log(email)
        try:
            result = email.send(fail_silently=False)
            return None, result
        except Exception, e:
            return e, result


    def log(self, data):
        print data
