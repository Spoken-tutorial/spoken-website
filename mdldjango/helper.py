
# Standard Library
import hashlib

# Third Party Stuff
from django.core.mail import EmailMultiAlternatives
from .models import MdlUser, MdlQuizGrades

# Spoken Tutorial Stuff
from events.models import *


def encript_password(password):
    password = hashlib.md5((password + 'VuilyKd*PmV?D~lO19jL(Hy4V/7T^G>p').encode('utf-8')).hexdigest()
    return password


def get_moodle_user(academic_id, firstname, lastname, gender, email):
    username = email
    mdluser = None
    try:
        mdluser = MdlUser.objects.filter(email = email).first()
        if not mdluser.institution == academic_id:
            mdluser.institution = academic_id
        if not mdluser.firstname == firstname:
            mdluser.firstname = firstname
        if not mdluser.lastname == lastname:
            mdluser.lastname = lastname
        if not mdluser.username == email:
            mdluser.username = email
        """password = encript_password(firstname)
        if not mdluser.password == password:
            mdluser.password = password"""
        mdluser.save()
    except Exception as e:
      print(f"No moodle user found : {e} - {email}\033[0m")
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
        mdluser.save()
        mdluser = MdlUser.objects.get(email=email)
      except Exception as e:
        print(f"exception during mdl user creation : {e} \033[0m")
    return mdluser


def get_moodle_grade(mdluserid, mdlquizid):
    mdlusergrade = MdlQuizGrades.objects.get(userid=mdluserid, quiz=mdlquizid)
    return mdlusergrade