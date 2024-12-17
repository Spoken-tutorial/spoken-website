# Third Party Stuff
from django import template
from django.contrib.auth.models import User

# Spoken Tutorial Stuff
from events.models import TestAttendance, TrainingAttendance
from mdldjango.models import *

register = template.Library()

def get_participant_score(key):
    try:
        ta = MdlUser.objects.get(mdluser_id = key)
    except:
        return 'error'
    
    return key

def check_training_enrole(rid, mdluser_id):
    try:
        wa = TrainingAttendance.objects.get(training_id = rid, mdluser_id = mdluser_id)
        return True
    except:
        return False

def check_test_enrole(rid, mdluser_id):
    try:
        wa = TestAttendance.objects.get(test_id = rid, mdluser_id = mdluser_id)
        return True
    except:
        return False

def get_participant_mark(rid, mdluser_id):
    try:
        ta = TestAttendance.objects.get(test_id = rid, mdluser_id = mdluser_id)
        if ta.mdlquiz_id:
            mdl = MdlQuizGrades.objects.filter(quiz = ta.mdlquiz_id, userid = mdluser_id).order_by('-grade').first()
            if mdl:
                return round(mdl.grade, 1)
            return False
    except TestAttendance.DoesNotExist:
        return False

def get_moodle_courseid(rid, mdluser_id):
    #print "rid =>", rid
    #print "mdluser =>", mdluser_id
    try:
        wa = TestAttendance.objects.get(test_id = rid, mdluser_id = mdluser_id)
        #print wa.mdlcourse_id
        return wa.mdlcourse_id
    except Exception as e:
        #print e
        return False

def get_mdluser_details(mdluser_id):
    try:
        mdluser = MdlUser.objects.get(id=mdluser_id)
        return mdluser
    except:
        return False
    
    
register.filter('get_participant_score', get_participant_score)
register.filter('get_participant_mark', get_participant_mark)
register.filter('check_training_enrole', check_training_enrole)
register.filter('check_test_enrole', check_test_enrole)
register.filter('get_moodle_courseid', get_moodle_courseid)
register.filter('get_mdluser_details', get_mdluser_details)
