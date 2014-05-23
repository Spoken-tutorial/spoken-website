from django import template
from django.contrib.auth.models import User
from mdldjango.models import *

register = template.Library()

def get_participant_score(key):
	try:
		ta = MdlUser.objects.get(mdluser_id = key)
	except:
		return 'error'
	
	return key


register.filter('get_participant_score', get_participant_score)
