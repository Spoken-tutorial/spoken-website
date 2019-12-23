# Standard Library
from builtins import str
import os
import zipfile
from urllib.parse import quote_plus
from urllib.request import urlopen

# Third Party Stuff
from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q

# Spoken Tutorial Stuff
from creation.models import *
from creation.views import (
    is_administrator,
    is_contenteditor,
    is_contributor,
    is_domainreviewer,
    is_external_contributor,
    is_internal_contributor,
    is_qualityreviewer,
    is_videoreviewer,
    is_language_manager
)
from spoken.forms import TutorialSearchForm

register = template.Library()

def format_component_title(name):
    return name.replace('_', ' ').capitalize()

def get_url_name(name):
    return quote_plus(name)

def get_zip_content(path):
    file_names = None
    try:
        zf = zipfile.ZipFile(path, 'r')
        file_names = zf.namelist()
        return file_names
    except Exception as e:
        return False

def is_script_available(path):
    try:
        code = urlopen(script_path).code
    except Exception as e:
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

def get_component_name(comp):
    comps = {
        1: 'Outline',
        2: 'Script',
        3: 'Video',
        4: 'Slides',
        5: 'Codefiles',
        6: 'Assignment'
    }
    key = ''
    try:
        key = comps[comp]
    except:
        pass
    return key.title()

def get_missing_component_reply(mcid):
    rows = TutorialMissingComponentReply.objects.filter(missing_component_id = mcid)
    replies = ''
    for row in rows:
        replies += '<p>' + row.reply_message + '<b> -' + row.user.username + '</b></p>'
    if replies:
        replies = '<br /><b>Replies:</b>' + replies
    return replies



def formatismp4(path):
    '''
    ** Registered to be used in jinja template **
    Function takes in a file name and checks if the 
    last 3 characters are `mp4`.
    '''
    return path[-3:] == 'mp4' or path[-3:] == 'mov'


def instruction_sheet(foss, lang):
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Instruction-Sheet-' + lang.name + '.pdf'
    if lang.name != 'English':
        if os.path.isfile(file_path):
            file_path = settings.MEDIA_URL + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Instruction-Sheet-' + lang.name + '.pdf'
            return file_path
    
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Instruction-Sheet-English.pdf'
    if os.path.isfile(file_path):
            file_path = settings.MEDIA_URL + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Instruction-Sheet-English.pdf'
            return file_path
    return False

def installation_sheet(foss, lang):
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Installation-Sheet-' + lang.name + '.pdf'
    if lang.name != 'English':
        if os.path.isfile(file_path):
            file_path = settings.MEDIA_URL + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Installation-Sheet-' + lang.name + '.pdf'
            return file_path
    
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Installation-Sheet-English.pdf'
    if os.path.isfile(file_path):
            file_path = settings.MEDIA_URL + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Installation-Sheet-English.pdf'
            return file_path
    return False
    
def brochure(foss, lang):
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Brochure-' + lang.name + '.pdf'
    if lang.name != 'English':
        if os.path.isfile(file_path):
            file_path = settings.MEDIA_URL + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Brochure-' + lang.name + '.pdf'
            return file_path
    
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Brochure-English.pdf'
    if os.path.isfile(file_path):
            file_path = settings.MEDIA_URL + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Brochure-English.pdf'
            return file_path
    return False

def get_thumb_path(row, append_str):
    path = settings.MEDIA_URL + 'videos/' + str(row.foss_id) + '/' + str(row.id) + '/' + row.tutorial.replace(' ', '-') + '-' + append_str + '.png'
    return path

def get_srt_path(tr):
    data = ''
    english_srt = settings.MEDIA_ROOT + 'videos/' + str(tr.tutorial_detail.foss_id) + '/' + str(tr.tutorial_detail_id) + '/' + tr.tutorial_detail.tutorial.replace(' ', '-') + '-English.srt'
    if os.path.isfile(english_srt):
        data = '<track kind="captions" src="'+ settings.MEDIA_URL + 'videos/' + str(tr.tutorial_detail.foss_id) + '/' + str(tr.tutorial_detail_id) + '/' + tr.tutorial_detail.tutorial.replace(' ', '-') + '-English.srt' + '" srclang="en" label="English"></track>'
    if tr.language.name != 'English':
        native_srt = settings.MEDIA_ROOT + 'videos/' + str(tr.tutorial_detail.foss_id) + '/' + str(tr.tutorial_detail_id) + '/' + tr.tutorial_detail.tutorial.replace(' ', '-') + '-' + tr.language.name +'.srt'
        print(native_srt)
        if os.path.isfile(native_srt):
            data += '<track kind="captions" src="'+ settings.MEDIA_URL + 'videos/' + str(tr.tutorial_detail.foss_id) + '/' + str(tr.tutorial_detail_id) + '/' + tr.tutorial_detail.tutorial.replace(' ', '-') + '-' + tr.language.name + '.srt' + '" srclang="en" label="' + tr.language.name + '"></track>'
    return data

def get_video_visits(tr):
    tr.hit_count = tr.hit_count + 1
    tr.save()
    return tr.hit_count

def get_prerequisite(tr, td):
    print((tr, td))
    try:
        tr_rec = TutorialResource.objects.get(Q(status = 1) | Q(status = 2), tutorial_detail = td, language_id = tr.language_id)
        return get_url_name(td.foss.foss) + '/' + get_url_name(td.tutorial) + '/' + tr_rec.language.name
    except Exception as e:
        print(e)
        if tr.language.name != 'English':
            try:
                tr_rec = TutorialResource.objects.get(Q(status = 1) | Q(status = 2), tutorial_detail = td, language__name = 'English')
                return get_url_name(td.foss.foss) + '/' + get_url_name(td.tutorial) + '/English'
            except:
                return None
        pass
    return None

def get_prerequisite_from_td(td, lang):
    try:
        tr_rec = TutorialResource.objects.get(Q(status = 1) | Q(status = 2), tutorial_detail = td, language_id = lang.id)
        return tr_rec.id
    except:
        if lang.name != 'English':
            try:
                tr_rec = TutorialResource.objects.get(Q(status = 1) | Q(status = 2), tutorial_detail = td, language__name = 'English')
                return tr_rec.id
            except:
                pass
    return None

def get_timed_script(script_path, timed_script_path):
    if timed_script_path:
        timed_script = settings.SCRIPT_URL + timed_script_path
    else:
        timed_script = settings.SCRIPT_URL + script_path + '-timed'
    print(script_path)
    code = 0
    try:
        code = urlopen(timed_script).code
    except Exception as e:
        timed_script = settings.SCRIPT_URL + \
            script_path.replace(' ', '-').replace('_', '-') + '-timed'
        print(timed_script)
        try:
            code = urlopen(timed_script).code
        except Exception as e:
            print((code, '----', e))
            code = 0
    if(int(code) == 200):
        return timed_script
    return ''

def tutorialsearch():
    context = {
        'form': TutorialSearchForm()
    }

    return context

def get_mp4_video(tr):
    video_name = tr.video
    splitat = -4
    tname, text = video_name[:splitat], video_name[splitat:]
    path = settings.MEDIA_ROOT + 'videos/' + str(tr.tutorial_detail.foss_id) + '/' + str(tr.tutorial_detail_id) + '/' + tname + '.mp4'
    if os.path.isfile(path):
        return 'videos/' + str(tr.tutorial_detail.foss_id) + '/' + str(tr.tutorial_detail_id) + '/' + tname + '.mp4'
    return False


register.inclusion_tag('spoken/templates/tutorial_search_form.html')(tutorialsearch)
#register.filter('tutorialsearch', tutorialsearch)
register.filter('get_timed_script', get_timed_script)
register.filter('formatismp4', formatismp4)
register.filter('get_prerequisite_from_td', get_prerequisite_from_td)
register.filter('get_prerequisite', get_prerequisite)
register.filter('get_video_visits', get_video_visits)
register.filter('get_srt_path', get_srt_path)
register.filter('get_thumb_path', get_thumb_path)
register.filter('get_missing_component_reply', get_missing_component_reply)
register.filter('get_component_name', get_component_name)
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
register.filter('instruction_sheet', instruction_sheet)
register.filter('installation_sheet', installation_sheet)
register.filter('brochure', brochure)
register.filter('get_contenteditor', is_contenteditor)
register.filter('format_component_title', format_component_title)
register.filter('get_mp4_video', get_mp4_video)
register.filter('get_language_manager',is_language_manager)