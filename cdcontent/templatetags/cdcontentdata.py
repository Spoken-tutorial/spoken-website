# Standard Library
import os

# Third Party Stuff
from django import template
from django.conf import settings

# Spoken Tutorial Stuff
from creation.models import *

register = template.Library()


def get_foss_name(foss, key):
    return foss[key]['foss']


def get_lang_details(foss, key):
    data = ''
    for lang_key, lang_detail in foss[key]['langs'].iteritems():
        data += '<option value="' + str(lang_key) + '">' + lang_detail + '</option>'
    return data

def cd_instruction_sheet(foss, lang):
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Instruction-Sheet-' + lang.name + '.pdf'
    if lang.name != 'English':
        if os.path.isfile(file_path):
            file_path = '../' + foss.foss.replace(' ', '-') + '-Instruction-Sheet-' + lang.name + '.pdf'
            return file_path


    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Instruction-Sheet-English.pdf'
    if os.path.isfile(file_path):
            file_path = '../' + foss.foss.replace(' ', '-') + '-Instruction-Sheet-English.pdf'
            return file_path
    return False

def rsplitpart (video):
    '''
    Takes arguement (example: ABC-Video.webm)
    and returns a trimmed version of it. (example: ABC-)
    ''' 
    return video.rsplit("Video")[0]


def cd_installation_sheet(foss, lang):
    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Installation-Sheet-' + lang.name + '.pdf'
    if lang.name != 'English':
        if os.path.isfile(file_path):
            file_path = '../' + foss.foss.replace(' ', '-') + '-Installation-Sheet-' + lang.name + '.pdf'
            return file_path

    file_path = settings.MEDIA_ROOT + 'videos/' + str(foss.id) + '/' + foss.foss.replace(' ', '-') + '-Installation-Sheet-English.pdf'
    if os.path.isfile(file_path):
            file_path = '../' + foss.foss.replace(' ', '-') + '-Installation-Sheet-English.pdf'
            return file_path
    return False


register.filter('rsplitpart', rsplitpart)
register.filter('get_foss_name', get_foss_name)
register.filter('get_lang_details', get_lang_details)
register.filter('cd_instruction_sheet', cd_instruction_sheet)
register.filter('cd_installation_sheet', cd_installation_sheet)
