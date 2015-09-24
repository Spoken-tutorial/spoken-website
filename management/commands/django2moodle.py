from django.core.management.base import BaseCommnd, CommandError
from django.contrib.auth.models import User

from hashlib import md5
from string import digits, ascii_uppercase
from random import sample


class Command(BaseCommand):
    help = 'Migrates user from django to moodle.\n\
            Send user credentials via email.'
    def handle(self, *args, **options):
        #logic
        '''
        get user from django
        check if user exist in moodle
        if user is student
        if not then
        get academy 
	 add in moodle
        then send email
        create log for each entry
        '''

    def get_spoken_user():
        return User.objects.all()


    def is_moodle_user(user):
        try:
            if MdlUser.objects.get(email=user.email):
                return True
        except MdlUser.DoesNotExist:
            return False


    def add_moodle_user(user, password, academy):
        ''' Creates moodle account and sends email'''
        mdluser = MdlUser()
        mdluser.firstname = user.firstname
        mdluser.lastname = user.lastname
        mdluser.username = user.email
        mdluser.password = encrypt_password(password)
        mdluser.institution = academy
        mdluser.gender = user.student.gender
        mdluser.confirmed = 1
        mdluser.mnethostid = 1
        mdluser.save()
        return mdluser


    def get

    def get_raw_password():
        return  ''.join(sample(ascii_uppercase + digits, 8))


    def encrypt_password(password):
        return md5(password+'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').hexdigest()


    def get_academy(user):
        return user.student.studentmaster_set.all().first().batch.organiser.academic

