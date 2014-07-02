import zipfile
from urllib import quote_plus
from django import template
from django.contrib.auth.models import User
from creation.models import *
from creation.views import is_contributor, is_internal_contributor, is_external_contributor, is_videoreviewer, is_domainreviewer, is_qualityreviewer, is_administrator

register = template.Library()

def get_url_name(name):
    return quote_plus(name)

def get_zip_content(path):
    file_names = None
    try:
        zf = zipfile.ZipFile(path, 'r')
        file_names = zf.namelist()
        return file_names
    except Exception, e:
        return False

def is_script_available(path):
    try:
        code = urlopen(script_path).code
    except Exception, e:
        code = e.code
    if(int(code) == 200):
        return True
    return False

def get_review_status_list(key):
	status_list = ['Pending', 'Waiting for Admin Review', 'Waiting for Domain Review', 'Waiting for Quality Review', 'Accepted', 'Need Improvement', 'Not Required']
	return status_list[key];

def get_review_status_class(key):
	status_list = ['danger', 'active', 'warning', 'info', 'success', 'danger', 'success']
	return status_list[key];

def get_review_status_symbol(key):
	status_list = ['fa fa-1 fa-minus-circle review-pending-upload', 'fa fa-1 fa-check-circle review-admin-review', 'fa fa-1 fa-check-circle review-domain-review', 'fa fa-1 fa-check-circle review-quality-review', 'fa fa-1 fa-check-circle review-accepted', 'fa fa-1 fa-times-circle review-pending-upload', 'fa fa-1 fa-ban review-accepted']
	return status_list[key];

def get_username(key):
	user = User.objects.get(pk = key)
	return user.username

def get_last_video_upload_time(key):
	rec = None
	try:
		rec = ContributorLog.objects.filter(tutorial_resource_id = key.id).order_by('-created')[0]
		tmpdt = key.updated
		for tmp in rec:
			tmpdt = rec.created
		return tmpdt
	except:
		return key.updated

register.filter('get_url_name', get_url_name)
register.filter('get_zip_content', get_zip_content)
register.filter('get_contributor', is_contributor)
register.filter('get_internal_contributor', is_internal_contributor)
register.filter('get_external_contributor', is_external_contributor)
register.filter('get_videoreviewer', is_videoreviewer)
register.filter('get_domainreviewer', is_domainreviewer)
register.filter('get_qualityreviewer', is_qualityreviewer)
register.filter('get_administrator', is_administrator)
register.filter('get_last_video_upload_time', get_last_video_upload_time)
register.filter('get_review_status_list', get_review_status_list)
register.filter('get_review_status_symbol', get_review_status_symbol)
register.filter('get_review_status_class', get_review_status_class)
register.filter('get_username', get_username)
