from django import template
from django.contrib.auth.models import User
from mdldjango.models import *
from events.models import TrainingAttendance, TestAttendance
from testapp.exam.models import AnswerPaper

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

def get_participant_mark(record, user):
    try:
        #for-exam-app
        if record.use_exam_app:
            ta = TestAttendance.objects.get(test_id = record.id, user_id = user.user_id)
            ans = AnswerPaper.objects.filter(question_paper_id = ta.examquestionpaper_id, user_id = user.user_id).order_by('-percent')
            if ans:
                return ans.first().percent
        else:
            ta = TestAttendance.objects.get(test_id = record.id, mdluser_id = user.mdluser_id)
    except Exception, e:
        print e
        return False
    
    if not ta.mdlquiz_id:
        return False
        
    try:
        mdlgrade = MdlQuizGrades.objects.get(quiz = ta.mdlquiz_id, userid = mdluser_id)
    except Exception, e:
        return False
        
    return round(mdlgrade.grade, 1)

def get_moodle_courseid(test, mdluser_id):
    try:
        #for-exam-app
        wa = False
        if test.use_exam_app:
            wa = TestAttendance.objects.get(test_id = test.id, user_id = mdluser_id)
        else:
            wa = TestAttendance.objects.get(test_id = test.id, mdluser_id = mdluser_id)
        print wa.id
        return wa
    except Exception, e:
        print e, "***********"
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
