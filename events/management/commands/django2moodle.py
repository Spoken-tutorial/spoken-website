# Standard Library
from datetime import datetime
from hashlib import md5
from random import sample
from string import ascii_uppercase, digits

# Third Party Stuff
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand

# Spoken Tutorial Stuff
from mdldjango.models import MdlUser


class Command(BaseCommand):
    help = 'Migrates user from django to moodle. Send user credentials via email.'
    FROM = 'administrator@spoken-tutorial.org'
    SUBJECT = "Spoken Tutorial Online Test password"
    HEADERS = {'Reply-To': 'no-replay@spoken-tutorial.org',
               "Content-type": "text/html;charset=iso-8859-1"}

    rmsg = 'Report {0}\n'.format(datetime.now())
    cmsg = 'Completed {0}\n'.format(datetime.now())
    imsg = 'Incomplete {0}\n'.format(datetime.now())

    def handle(self, *args, **options):
        users = self.get_spoken_user()
        self.log('Total users: {0}'.format(users.count()), 'r')
        count = 0
        ncount = 0

        for user in users:
            self.log('\n###############\n', 'i')
            if self.is_student(user):
                self.log('\n###############\n', 'c')
                self.log(user, 'c')
                if not self. is_moodle_user(user):
                    try:
                        self.log('email: {0} not in moodle'.format(user.email.encode('utf8')), 'c')
                    except:
                        print user.email
                        pass
                    academy = self.get_academy(user)
                    if academy:
                        self.log('Academy {0}'.format(academy), 'c')
                        password = self.get_raw_password()
                        self.log('Password ' + password, 'c')
                        mdluser = self.add_moodle_user(user, password, academy)
                        if mdluser:
                            self.log("Added to moodle", 'c')
                            ex, res = self.send_email(mdluser, password)
                            self.log(res, 'c')
                            self.log(res, 'i')
                            if ex:
                                self.log(ex, 'i')
                                ncount += 1
                                break
                            count += 1
                        else:
                            self.log("user not added", 'i')
                            ncount += 1
                    else:
                        self.log("no academy", 'i')
                        ncount += 1
                else:
                    self.log('Email: {0} in moodle'.format(user.email.encode('utf8')), 'i')
                    ncount += 1
            else:
                self.log('{0} not student'.format(user), 'i')
                ncount += 1

        self.log('Added and Mailed:{0}'.format(count), 'r')
        self.log('Not added: {0}'.format(ncount), 'r')

        self.create_log_file(self.cmsg, 'c')
        self.create_log_file(self.imsg, 'i')
        err_value = self.create_log_file(self.rmsg, 'r')
        if err_value:
            self.stdout.write(self.cmsg)
            self.stdout.write(self.imsg)
            self.stdout.write(self.rmsg)

    def get_spoken_user(self):
        return User.objects.filter(id=333224)

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
        except Exception, e:
            print e
            return True

    def get_academy(self, user):
        try:
            return user.student.studentmaster_set.all().first().batch.organiser.academic
        except AttributeError:
            return None

    def add_moodle_user(self, user, password, academy):
        ''' Creates moodle account and sends email'''
        try:
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
        except Exception, e:
            print e
            return None

    def get_raw_password(self):
        return ''.join(sample(ascii_uppercase + digits, 8))

    def encrypt_password(self, password):
        return md5(password + 'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()

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
        message = message.format(user.firstname.encode('utf8'), user.username.encode('utf8'), password)
        self.log(message, 'c')
        email = EmailMultiAlternatives(self.SUBJECT, message, self.FROM,
                                       to=[user.email], bcc=[], cc=[], headers=self.HEADERS)
        self.log(email, 'c')
        try:
            result = email.send(fail_silently=False)
            return None, result
        except Exception, e:
            return e, result

    def log(self, data, _type):
        try:
            if _type == 'c':
                self.cmsg = '{0} {1}\n'.format(self.cmsg, data)
            if _type == 'i':
                self.imsg = '{0} {1}\n'.format(self.imsg, data)
            if _type == 'r':
                self.rmsg = '{0} {1}\n'.format(self.rmsg, data)
        except Exception as e:
            print(e)

    def create_log_file(self, data, _type):
        try:
            if _type == 'c':
                _file = open('migrated.log', 'ab+')
            if _type == 'i':
                _file = open('not_migrated.log', 'ab+')
            if _type == 'r':
                _file = open('report.log', 'ab+')

            _file.write('\n{0}\n'.format(data))
            _file.close()
        except Exception as e:
            return e
