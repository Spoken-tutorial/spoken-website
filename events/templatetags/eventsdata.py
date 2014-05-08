from django import template
from django.contrib.auth.models import User
from events.models import *

register = template.Library()

def get_participant_status(key, testcode):
	status_list = ['Waitin for Attendance', 'Ready to enter in to test', 'Entered in to test', 'Completed', 'Got certificate']
	try:
		ta = TestAttendance.objects.get(mdluser_id=key, test_id=testcode)
	except:
		return 'error'
	return status_list[ta.status]

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

def can_close_test(testcode):
	try:
		ta = TestAttendance.objects.filter(test_id = testcode, status__range=(0, 3)).first()
	except:
		return True
	return False
	
register.filter('get_status', get_status)
register.filter('can_close_test', can_close_test)
register.filter('get_participant_status', get_participant_status)
