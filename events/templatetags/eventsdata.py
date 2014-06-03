from django import template
from django.contrib.auth.models import User
from events.models import *
from events.views import is_organiser, is_invigilator, is_resource_person, is_event_manager
import datetime
register = template.Library()

def get_participant_status(key, testcode):
    status_list = ['Waiting for Attendance', 'Ready to enter in to test', 'Entered in to test', 'Completed', 'Got certificate']
    try:
        ta = TestAttendance.objects.get(mdluser_id=key, test_id=testcode)
    except:
        return 'Add'
    return status_list[ta.status]

def get_wparticipant_status(key, wcode):
    status_list = ['Waiting for Attendance', 'Completed', 'Got certificate']
    try:
        wa = WorkshopAttendance.objects.get(mdluser_id=key, workshop_id = wcode)
    except:
        return 'error'
    return status_list[wa.status]

def get_trainingparticipant_status(key, wcode):
    status_list = ['Waiting for Attendance', 'Completed', 'Got certificate']
    try:
        wa = TrainingAttendance.objects.get(mdluser_id=key, training_id = wcode)
    except:
        return 'error'
    return status_list[wa.status]

def get_status(key, testcode):
    try:
        ta = TestAttendance.objects.get(mdluser_id=key, test_id=testcode)
    except:
        return 'error'
    
    if ta.status == 1:
        return 'checked'
    
    if ta.status > 1:
        return 'disabled=disabled checked'
    
    return ''

def can_enter_test(key, testcode):
    try:
        ta = TestAttendance.objects.get(mdluser_id=key, test_id=testcode)
    except:
        return None
    if ta.status >= 0:
        return ta.status
    return None

def get_wstatus(key, wcode):
    try:
        wa = WorkshopAttendance.objects.get(mdluser_id=key, workshop_id = wcode)
    except:
        return ''
    
    if wa.status == 1:
        return 'checked'
    
    if wa.status > 1:
        return 'disabled=disabled checked'
    
    return ''

def get_trainingstatus(key, wcode):
    try:
        wa = TrainingAttendance.objects.get(mdluser_id=key, training_id = wcode)
    except:
        return ''
    
    if wa.status == 1:
        return 'checked'
    
    if wa.status > 1:
        return 'disabled=disabled checked'
    
    return ''

def can_close_test(testcode):
    try:
        ta = TestAttendance.objects.filter(test_id = testcode, status__range=(0, 3)).first()
    except:
        return True
    return False
def can_upload_workshop_data(wcode, category):
    if category == 'workshop':
        try:
            w = Workshop.objects.get(pk=wcode)
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")
            wdate = w.wdate.strftime("%Y-%m-%d")
            if wdate <= today_date:
                return True
            return False
        except Exception, e:
            print e
            return False
    if category == 'training':
        try:
            w = Training.objects.get(pk=wcode)
            today_date = datetime.datetime.now().strftime("%Y-%m-%d")
            wdate = w.trdate.strftime("%Y-%m-%d")
            if wdate <= today_date:
                return True
            return False
        except Exception, e:
            print e
            return False
    
register.filter('is_organiser', is_organiser)
register.filter('is_invigilator', is_invigilator)
register.filter('is_resource_person', is_resource_person)
register.filter('is_event_manager', is_event_manager)

register.filter('can_enter_test', can_enter_test)
register.filter('get_status', get_status)
register.filter('get_wstatus', get_wstatus)
register.filter('get_trainingstatus', get_trainingstatus)
register.filter('can_close_test', can_close_test)
register.filter('get_participant_status', get_participant_status)
register.filter('get_wparticipant_status', get_wparticipant_status)
register.filter('get_trainingparticipant_status', get_trainingparticipant_status)
register.filter('can_upload_workshop_data', can_upload_workshop_data)
