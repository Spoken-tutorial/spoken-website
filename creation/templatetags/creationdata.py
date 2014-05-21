from django import template
from django.contrib.auth.models import User
from creation.models import *

register = template.Library()

def get_review_status_list(key):
	status_list = ['Pending', 'Waiting for Admin Review', 'Waiting for Domain Review', 'Waiting for Quality Review', 'Accepted', 'Need Improvement']
	return status_list[key];

def get_review_status_class(key):
	status_list = ['danger', 'active', 'warning', 'info', 'success', 'danger']
	return status_list[key];

def get_review_status_symbol(key):
	status_list = ['fa fa-1 fa-minus-circle review-pending-upload', 'fa fa-1 fa-check-circle review-admin-review', 'fa fa-1 fa-check-circle review-domain-review', 'fa fa-1 fa-check-circle review-quality-review', 'fa fa-1 fa-check-circle review-accepted', 'fa fa-1 fa-times-circle review-pending-upload']
	return status_list[key];

def get_username(key):
	user = User.objects.get(pk = key)
	return user.username

def get_last_video_upload_time(key):
	rec = None
	try:
		rec = Contributor_Log.objects.filter(tutorial_resource_id = key.id).order_by('-created')[0]
		tmpdt = key.updated
		for tmp in rec:
			tmpdt = rec.created
		return tmpdt
	except:
		return key.updated

register.filter('get_last_video_upload_time', get_last_video_upload_time)
register.filter('get_review_status_list', get_review_status_list)
register.filter('get_review_status_symbol', get_review_status_symbol)
register.filter('get_review_status_class', get_review_status_class)
register.filter('get_username', get_username)
