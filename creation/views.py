# Standard Library
import json
import os
import re
import subprocess
import time
from django.utils import timezone
from decimal import Decimal
from urllib import quote, unquote_plus, urlopen

# Third Party Stuff
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Spoken Tutorial Stuff
from cms.sortable import *
from creation.forms import *
from creation.models import *
from creation.subtitles import *

from . import services


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.1f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

def get_page(resource, page, page_count = 20):
    paginator = Paginator(resource, page_count)
    try:
        resource =  paginator.page(page)
    except PageNotAnInteger:
        resource =  paginator.page(1)
    except EmptyPage:
        resource = paginator.page(paginator.num_pages)
    return resource


def is_contributor(user):
    """Check if the user is having contributor rights"""
    if user.groups.filter(Q(name='Contributor')|Q(name='External-Contributor')).count():
        return True
    return False

def is_internal_contributor(user):
    """Check if the user is having contributor rights"""
    if user.groups.filter(name='Contributor').count():
        return True
    return False

def is_external_contributor(user):
    """Check if the user is having external-contributor rights"""
    if user.groups.filter(name='External-Contributor').count():
        return True
    return False

def is_videoreviewer(user):
    """Check if the user is having video reviewer rights"""
    if user.groups.filter(name='Video-Reviewer').count() == 1:
        return True
    return False

def is_domainreviewer(user):
    """Check if the user is having domain reviewer rights"""
    if user.groups.filter(name='Domain-Reviewer').count() == 1:
        return True
    return False

def is_qualityreviewer(user):
    """Check if the user is having quality reviewer rights"""
    if user.groups.filter(name='Quality-Reviewer').count() == 1:
        return True
    return False

def is_administrator(user):
    """Check if the user is having administrator rights"""
    if user.groups.filter(name='Administrator').count():
        return True
    return False

def is_contenteditor(user):
    """Check if the user is having Content-Editor rights"""
    if user.groups.filter(name='Content-Editor').count():
        return True
    return False

def get_filesize(path):
    filesize_bytes = os.path.getsize(path)
    return humansize(filesize_bytes)


def get_audio_info(path):
    """
    Uses FFmpeg to determine information about an audio file.
    Information displayed on admin_review page is generated from here.
    """
    info_m = {}
    try:
        process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        duration_m = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?)", stdout, re.DOTALL).groupdict()
        info_m = re.search(r": Audio: (?P<codec>.*?), (?P<profile>.*?)", stdout, re.DOTALL).groupdict()
        
        hours = Decimal(duration_m['hours'])
        minutes = Decimal(duration_m['minutes'])
        seconds = Decimal(duration_m['seconds'])

        total = 0
        total += 60 * 60 * hours
        total += 60 * minutes
        total += seconds

        info_m['hours'] = hours
        info_m['minutes'] = minutes
        info_m['seconds'] = seconds
        tmp_seconds = str(int(seconds))
        if seconds < 10:
            tmp_seconds = "0" + tmp_seconds
        info_m['duration'] = duration_m['hours'] + ':' + duration_m['minutes'] + ":" + tmp_seconds
        info_m['total'] = int(total)
        info_m['size'] = get_filesize(path)
    except:
        info_m['hours'] = 0
        info_m['minutes'] = 0
        info_m['seconds'] = 0
        info_m['duration'] = 0
        info_m['total'] = 0
        info_m['size'] = 0
    return info_m


def get_video_info(path):
    """
    Uses ffmpeg to determine information about a video.
    Information displayed on admin_review page is generated from here.
    """
    info_m = {}
    try:
        process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        duration_m = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?)", stdout, re.DOTALL).groupdict()
        info_m = re.search(r": Video: (?P<codec>.*?), (?P<profile>.*?), (?P<width>.*?)x(?P<height>.*?), ", stdout, re.DOTALL).groupdict()

        hours = Decimal(duration_m['hours'])
        minutes = Decimal(duration_m['minutes'])
        seconds = Decimal(duration_m['seconds'])

        total = 0
        total += 60 * 60 * hours
        total += 60 * minutes
        total += seconds

        info_m['hours'] = hours
        info_m['minutes'] = minutes
        info_m['seconds'] = seconds
        tmp_seconds = str(int(seconds))
        if seconds < 10:
            tmp_seconds = "0" + tmp_seconds
        info_m['duration'] = duration_m['hours'] + ':' + duration_m['minutes'] + ":" + tmp_seconds
        info_m['total'] = int(total)
        info_m['width'] = int(info_m['width'])
        # [PAR 1i:1 DAR 3:2] error in height
        info_m['height'] = int(info_m['height'].split()[0])
        info_m['size'] = get_filesize(path)
    except:
        info_m['codec'] = ''
        info_m['profile'] = ''
        info_m['hours'] = 0
        info_m['minutes'] = 0
        info_m['seconds'] = 0
        info_m['duration'] = 0
        info_m['total'] = 0
        info_m['width'] = 0
        info_m['height'] = 0
        info_m['size'] = 0
    return info_m


#create_thumbnail(tr_rec, 'Big', tr_rec.audio_thumbnail_time, '700:500')
def create_thumbnail(row, attach_str, thumb_time, thumb_size):
    filepath = settings.MEDIA_ROOT + 'videos/' + str(row.tutorial_detail.foss_id) + '/' + str(row.tutorial_detail_id) + '/'
    filename = row.tutorial_detail.tutorial.replace(' ', '-') + '-' + attach_str + '.png'
    try:
        #process = subprocess.Popen(['/usr/bin/ffmpeg', '-i ' + filepath + row.video + ' -r ' + str(30) + ' -ss ' + str(thumb_time) + ' -s ' + thumb_size + ' -vframes ' + str(1) + ' -f ' + 'image2 ' + filepath + filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', filepath + row.video, '-r', str(30), '-ss', str(thumb_time), '-s', thumb_size, '-vframes', str(1), '-f', 'image2', filepath + filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = process.communicate()
        if stderr:
            print filepath + filename
            print stderr
    except Exception, e:
        print 1, e
        pass


def add_qualityreviewer_notification(tr_rec, comp_title, message):
    dr_roles = QualityReviewerRole.objects.filter(foss_category = tr_rec.tutorial_detail.foss, language = tr_rec.language, status = 1)
    for dr_role in dr_roles:
        QualityReviewerNotification.objects.create(user = dr_role.user, title = comp_title, message = message, tutorial_resource = tr_rec)

def add_domainreviewer_notification(tr_rec, comp_title, message):
    dr_roles = DomainReviewerRole.objects.filter(foss_category = tr_rec.tutorial_detail.foss, language = tr_rec.language, status = 1)
    for dr_role in dr_roles:
        DomainReviewerNotification.objects.create(user = dr_role.user, title = comp_title, message = message, tutorial_resource = tr_rec)

def add_adminreviewer_notification(tr_rec, comp_title, message):
    role = Group.objects.get(name = 'Video-Reviewer')
    users = role.user_set.all()

    for user in users:
        AdminReviewerNotification.objects.create(user = user, title = comp_title, message = message, tutorial_resource = tr_rec)

def add_contributor_notification(tr_rec, comp_title, message):
    con_roles = ContributorRole.objects.filter(foss_category = tr_rec.tutorial_detail.foss, language = tr_rec.language, status = 1)

    for con in con_roles:
        ContributorNotification.objects.create(user = con.user, title = comp_title, message = message, tutorial_resource = tr_rec)

@login_required
def creation_add_role(request, role_type):
    flag = 1
    roles = {
        'contributor': 0,
        'external-contributor': 1,
        'video-reviewer': 2,
        'domain-reviewer': 3,
        'quality-reviewer': 4,
    }
    if role_type in roles:
        try:
            RoleRequest.objects.create(user = request.user, role_type = roles[role_type], status = 0)
        except:
            try:
                role_rec = RoleRequest.objects.get(user = request.user, role_type = roles[role_type], status = 2)
                role_rec.status = 0
                role_rec.save()
            except:
                flag = 0
                messages.warning(request, 'Request to the ' + role_type.title() + ' role is already waiting for admin approval!')
    else:
        flag = 0
        messages.error(request, 'Invalid role argument!')
    if flag:
        messages.success(request, 'Request to the ' + role_type.title() + ' role has been sent for admin approval!')
    return HttpResponseRedirect('/creation/')

@login_required
def creation_accept_role_request(request, recid):
    if is_administrator:
        roles = {
            0: 'Contributor',
            1: 'External-Contributor',
            2: 'Video-Reviewer',
            3: 'Domain-Reviewer',
            4: 'Quality-Reviewer',
        }
        try:
            role_rec = RoleRequest.objects.get(pk = recid, status = 0)
            if role_rec.role_type in roles:
                try:
                    role_rec.user.groups.add(Group.objects.get(name = roles[role_rec.role_type]))
                    role_rec.approved_user = request.user
                    role_rec.status = 1
                    role_rec.save()
                    messages.success(request, roles[role_rec.role_type] + ' role is added to ' + role_rec.user.username)
                except:
                    messages.error(request, role_rec.user.username + ' is already having ' + roles[role_rec.role_type] + ' role.')
            else:
                messages.error(request, 'Invalid role argument!')
        except:
            messages.error(request, 'The given role request id is either invalid or it is already accepted')
    else:
        raise PermissionDenied()
    return HttpResponseRedirect('/creation/role/requests/' + roles[role_rec.role_type].lower() + '/')

@login_required
def creation_reject_role_request(request, recid):
    if is_administrator:
        print "test 2"
        roles = {
            0: 'Contributor',
            1: 'External-Contributor',
            2: 'Video-Reviewer',
            3: 'Domain-Reviewer',
            4: 'Quality-Reviewer',
        }
        try:
            role_rec = RoleRequest.objects.get(pk = recid, status = 0)
            role_rec.delete()
            messages.success(request, 'Selected role request has been deleted successfully!')
        except:
            messages.error(request, 'The given role request id is either invalid or it is already reject')
    else:
        raise PermissionDenied()
    return HttpResponseRedirect('/creation/role/requests/' + roles[role_rec.role_type].lower() + '/')

@login_required
def creation_revoke_role_request(request, role_type):
    roles = {
        'contributor': 0,
        'external-contributor': 1,
        'video-reviewer': 2,
        'domain-reviewer': 3,
        'quality-reviewer': 4,
    }
    if role_type in roles:
        try:
            role_rec = RoleRequest.objects.get(user = request.user, role_type = roles[role_type], status = 1)
            if role_rec.role_type != 2:
                if role_rec.role_type == 0 or role_rec.role_type == 1:
                    ContributorRole.objects.filter(user = role_rec.user).update(status = 0)
                elif role_rec.role_type == 3:
                    DomainReviewerRole.objects.filter(user = role_rec.user).update(status = 0)
                elif role_rec.role_type == 4:
                    QualityReviewerRole.objects.filter(user = role_rec.user).update(status = 0)
                role_rec.user.groups.remove(Group.objects.get(name = role_type.title()))
                role_rec.status = 2
                role_rec.save()
                messages.success(request, role_type.title() + ' role has been revoked from ' + role_rec.user.username)
        except:
            raise PermissionDenied()
    else:
        messages.error(request, 'Invalid role type argument!')
    return HttpResponseRedirect('/creation/')

@login_required
def creation_list_role_requests(request, tabid = 'contributor'):
    if is_administrator:
        contrib_recs = RoleRequest.objects.filter(role_type = 0, status = 0).order_by('-updated')
        ext_contrib_recs = RoleRequest.objects.filter(role_type = 1, status = 0).order_by('-updated')
        admin_recs = RoleRequest.objects.filter(role_type = 2, status = 0).order_by('-updated')
        domain_recs = RoleRequest.objects.filter(role_type = 3, status = 0).order_by('-updated')
        quality_recs = RoleRequest.objects.filter(role_type = 4, status = 0).order_by('-updated')
        context = {
            'tabid': tabid,
            'contrib_recs': contrib_recs,
            'ext_contrib_recs': ext_contrib_recs,
            'admin_recs': admin_recs,
            'domain_recs': domain_recs,
            'quality_recs': quality_recs,
        }
        return render(request, 'creation/templates/creation_list_role_requests.html', context)
    else:
        raise PermissionDenied()

@login_required
def init_creation_app(request):
    try:
        if Group.objects.filter(name = 'Contributor').count() == 0:
            Group.objects.create(name = 'Contributor')
        if Group.objects.filter(name = 'External-Contributor').count() == 0:
            Group.objects.create(name = 'External-Contributor')
        if Group.objects.filter(name = 'Video-Reviewer').count() == 0:
            Group.objects.create(name = 'Video-Reviewer')
        if Group.objects.filter(name = 'Domain-Reviewer').count() == 0:
            Group.objects.create(name = 'Domain-Reviewer')
        if Group.objects.filter(name = 'Quality-Reviewer').count() == 0:
            Group.objects.create(name = 'Quality-Reviewer')
        if Group.objects.filter(name = 'Quality-Reviewer').count() == 0:
            Group.objects.create(name = 'Quality-Reviewer')
        if Group.objects.filter(name = 'Administrator').count() == 0:
            Group.objects.create(name = 'Administrator')
        messages.success(request, 'Creation application initialised successfully!')
    except Exception, e:
        messages.error(request, str(e))
    return HttpResponseRedirect('/creation/')

# Creation app dashboard
@login_required
def creationhome(request):
    if is_contributor(request.user) or is_domainreviewer(request.user) or is_videoreviewer(request.user) or is_qualityreviewer(request.user):
        contrib_notifs = []
        admin_notifs = []
        domain_notifs = []
        quality_notifs = []
        if is_contributor(request.user):
            contrib_notifs = ContributorNotification.objects.filter(user = request.user).order_by('-created')
        if is_videoreviewer(request.user):
            admin_notifs = AdminReviewerNotification.objects.filter(user = request.user).order_by('-created')
        if is_domainreviewer(request.user):
            domain_notifs = DomainReviewerNotification.objects.filter(user = request.user).order_by('-created')
        if is_qualityreviewer(request.user):
            quality_notifs = QualityReviewerNotification.objects.filter(user = request.user).order_by('-created')
        context = {
            'contrib_notifs': contrib_notifs,
            'admin_notifs': admin_notifs,
            'domain_notifs': domain_notifs,
            'quality_notifs': quality_notifs,
            'is_creation_role': True
        }
        context.update(csrf(request))
        return render(request, 'creation/templates/creationhome.html', context)
    else:
        context = {
            'is_creation_role': False
        }
        return render(request, 'creation/templates/creationhome.html', context)

# tutorial upload index page
@login_required
def upload_index(request):
    if not is_contributor(request.user):
        raise PermissionDenied()
    if request.method == 'POST':
        form = UploadTutorialForm(request.user, request.POST)
        if form.is_valid():
            common_content = TutorialCommonContent()
            if TutorialCommonContent.objects.filter(tutorial_detail_id = request.POST['tutorial_name']).count():
                common_content = TutorialCommonContent.objects.get(tutorial_detail_id = request.POST['tutorial_name'])
            else:
                common_content.tutorial_detail = TutorialDetail.objects.get(pk = request.POST['tutorial_name'])
                common_content.slide_user = request.user
                common_content.code_user = request.user
                common_content.assignment_user = request.user
                common_content.prerequisite_user = request.user
                common_content.keyword_user = request.user
                common_content.save()
            if TutorialResource.objects.filter(tutorial_detail_id = request.POST['tutorial_name'], common_content_id = common_content.id, language_id = request.POST['language']).count():
                tutorial_resource = TutorialResource.objects.get(tutorial_detail_id = request.POST['tutorial_name'], common_content_id = common_content.id, language_id = request.POST['language'])
            else:
                tutorial_resource = TutorialResource()
                tutorial_resource.tutorial_detail = common_content.tutorial_detail
                tutorial_resource.common_content = common_content
                tutorial_resource.language_id = request.POST['language']
                tutorial_resource.outline_user = request.user
                tutorial_resource.script_user = request.user
                tutorial_resource.video_user = request.user
                tutorial_resource.audio = "Unavailable"
                tutorial_resource.save()

            return HttpResponseRedirect('/creation/upload/tutorial/' + str(tutorial_resource.id) + '/')
    else:
        form = UploadTutorialForm(user=request.user)

    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_index.html', context)

def upload_publish_outline(request):
    if not is_contributor(request.user):
        raise PermissionDenied()
    if request.method == 'POST':
        form = UploadPublishTutorialForm(request.user, request.POST)
        if form.is_valid():
            tutorial_resource = TutorialResource.objects.get(tutorial_detail_id = request.POST['tutorial_name'], language_id = request.POST['language'])
            return HttpResponseRedirect('/creation/upload/outline/' + str(tutorial_resource.id) + '/?publish=1')
    else:
        form = UploadPublishTutorialForm(user=request.user)

    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload-publish-script.html', context)

@csrf_exempt
def ajax_upload_prerequisite(request):
    data = ''
    if request.method == 'POST':
        foss = ''
        try:
            foss = int(request.POST.get('foss'))
            lang_rec = Language.objects.get(name = 'English')
        except:
            foss = ''
        if foss and lang_rec:
            td_list = TutorialDetail.objects.filter(foss_id = foss).values_list('id')
            td_recs = TutorialDetail.objects.filter(
                id__in = TutorialResource.objects.filter(
                    tutorial_detail_id__in = td_list,
                    language_id = lang_rec.id,
                ).values_list(
                    'tutorial_detail_id'
                )
            ).order_by('tutorial')
            for td_rec in td_recs:
                data += '<option value="' + str(td_rec.id) + '">' + td_rec.tutorial + '</option>'
            if data:
                data = '<option value="">Select Tutorial</option>' + data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def ajax_upload_foss(request):
    data = ''
    if request.method == 'POST':
        foss = ''
        lang = ''
        publish = request.POST.get('publish', False)
        try:
            foss = request.POST.get('foss')
            lang = request.POST.get('lang')
        except:
            foss = ''
            lang = ''
        if foss and lang and publish:
            lang_rec = Language.objects.get(pk = int(lang))
            if lang_rec.name == 'English':
                td_list = TutorialDetail.objects.filter(foss_id = foss).values_list('id')
                tutorials = TutorialDetail.objects.filter(
                    id__in = td_list
                )
            else:
                eng_rec = Language.objects.get(name = 'English')
                td_list = TutorialDetail.objects.filter(foss_id = foss).values_list('id')
                tutorials = TutorialDetail.objects.filter(
                    id__in = TutorialResource.objects.filter(
                        tutorial_detail_id__in = td_list,
                        language_id = eng_rec.id,
                        status = 1
                    ).values_list(
                        'tutorial_detail_id'
                    )
                )
            for tutorial in tutorials:
                data += '<option value="' + str(tutorial.id) + '">' + tutorial.tutorial + '</option>'
            if data:
                data = '<option value="">Select Tutorial</option>' + data
        elif foss and lang:
            lang_rec = Language.objects.get(pk = int(lang))
            if lang_rec.name == 'English':
                td_list = TutorialDetail.objects.filter(foss_id = foss).values_list('id')
                tutorials = TutorialDetail.objects.filter(
                    id__in = td_list
                ).exclude(
                    id__in = TutorialResource.objects.filter(
                        tutorial_detail_id__in = td_list,
                        language_id = lang_rec.id,
                        status = 1
                    ).values_list(
                        'tutorial_detail_id'
                    )
                )
            else:
                eng_rec = Language.objects.get(name = 'English')
                td_list = TutorialDetail.objects.filter(foss_id = foss).values_list('id')
                tutorials = TutorialDetail.objects.filter(
                    id__in = TutorialResource.objects.filter(
                        tutorial_detail_id__in = td_list,
                        language_id = eng_rec.id,
                        status = 1
                    ).values_list(
                        'tutorial_detail_id'
                    )
                ).exclude(
                    id__in = TutorialResource.objects.filter(
                        tutorial_detail_id__in = td_list,
                        language_id = lang_rec.id,
                        status__gte = 1
                    ).values_list(
                        'tutorial_detail_id'
                    )
                )
            for tutorial in tutorials:
                data += '<option value="' + str(tutorial.id) + '">' + tutorial.tutorial + '</option>'
            if data:
                data = '<option value="">Select Tutorial</option>' + data
        elif foss:
            languages = Language.objects.filter(id__in = ContributorRole.objects.filter(user_id = request.user.id, foss_category_id = foss).values_list('language_id'))
            for language in languages:
                data += '<option value="' + str(language.id) + '">' + language.name + '</option>'
            if data:
                data = '<option value="">Select Language</option>' + data

    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def ajax_get_keywords(request):
    data = ''
    if request.method == 'POST':
        try:
            tutorial_detail_id = int(request.POST.get('tutorial_detail'))
            tcc = TutorialCommonContent.objects.get(tutorial_detail_id = tutorial_detail_id)
            data = tcc.keyword
        except Exception, e:
            pass
    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def upload_tutorial(request, trid):
    tr_rec = None
    contrib_log = None
    review_log = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        ContributorRole.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
        contrib_log = ContributorLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_log = NeedImprovementLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
    except Exception, e:
        print e
        raise PermissionDenied()
    file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/' + tr_rec.audio
    if os.path.isfile(file_path) == False:
        tr_rec.audio = "Unavailable"
        tr_rec.save()
    context = {
        'tr': tr_rec,
        'contrib_log': contrib_log,
        'review_log': review_log,
        'script_base': settings.SCRIPT_URL,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_tutorial.html', context)

@login_required
def upload_outline(request, trid):
    tr_rec = None
    publish = int(request.GET.get('publish', 0))
    try:
        status = 0
        if publish:
            status = 1
        tr_rec = TutorialResource.objects.get(pk = trid, status = status)
        ContributorRole.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        raise PermissionDenied()
    if not publish and tr_rec.outline_status > 2 and tr_rec.outline_status != 5:
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    warning_msg = ''
    if request.method == 'POST':
        form = UploadOutlineForm(trid, request.POST)
        if form.is_valid():
            try:
                prev_state = tr_rec.outline_status
                if tr_rec.outline != request.POST['outline']:
                    tr_rec.outline = request.POST['outline']
                else:
                    warning_msg = 'There is no change in outline'
                if publish:
                    tr_rec.save()
                    messages.success(request, "Outline status updated successfully!")
                    return HttpResponseRedirect('/creation/upload-publish-outline/')
                tr_rec.outline_user = request.user
                tr_rec.outline_status = 2
                tr_rec.save()
                ContributorLog.objects.create(status = prev_state, user = request.user, tutorial_resource = tr_rec, component = 'outline')
                comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
                add_domainreviewer_notification(tr_rec, comp_title, 'Outline waiting for Domain review')
                response_msg = 'Outline status updated successfully!'
            except Exception, e:
                print e
                error_msg = 'Something went wrong, please try again later.'
        else:
            context = {
                'form': form,
            }
            context.update(csrf(request))
            return render(request, 'creation/templates/upload_outline.html', context)
    form = UploadOutlineForm(trid)
    if response_msg:
        messages.success(request, response_msg)
    if error_msg:
        messages.error(request, error_msg)
    if warning_msg:
        messages.warning(request, warning_msg)
    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_outline.html', context)

@login_required
def upload_script(request, trid):
    tr_rec = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        ContributorRole.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        raise PermissionDenied()
    if tr_rec.script_status > 2 and tr_rec.script_status != 5:
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    storage_path = tr_rec.tutorial_detail.foss.foss.replace(' ', '-') + '/' + tr_rec.tutorial_detail.level.code + '/' + tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '/' + tr_rec.language.name
    script_path = settings.SCRIPT_URL + storage_path
    if request.method == 'POST':
        form = UploadScriptForm(script_path, request.POST)
        if form.is_valid():
            try:
                code = 0
                try:
                    code = urlopen(script_path).code
                except Exception, e:
                    code = e.code
                if(int(code) == 200):
                    prev_state = tr_rec.script_status
                    tr_rec.script = storage_path
                    tr_rec.script_user = request.user
                    tr_rec.script_status = 2
                    tr_rec.save()
                    ContributorLog.objects.create(status = prev_state, user = request.user, tutorial_resource = tr_rec, component = 'script')
                    comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
                    add_domainreviewer_notification(tr_rec, comp_title, 'Script waiting for domain review')
                    response_msg = 'Script status updated successfully'
                else:
                    error_msg = 'Please update the script to wiki before pressing the submit button.'
            except Exception, e:
                print e
                error_msg = 'Something went wrong, please try again later.'
        else:
            context = {
                'form': form,
                'script_path': script_path,
            }
            context.update(csrf(request))
            return render(request, 'creation/templates/upload_script.html', context)
    form = UploadScriptForm(script_path)
    if error_msg:
        messages.error(request, error_msg)
    if response_msg:
        messages.success(request, response_msg)
    context = {
        'form': form,
        'script_path': script_path,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_script.html', context)

@login_required
def upload_timed_script(request):
    if not is_contributor(request.user):
        raise PermissionDenied()
    form = UploadTimedScriptForm(request.user)
    if request.method == 'POST':
        form = UploadTimedScriptForm(request.user, request.POST)
        lang = None
        if form.is_valid():
            try:
                return HttpResponseRedirect('/creation/upload/timed-script/' + request.POST.get('tutorial_name') + '/save/')
            except Exception, e:
                messages.error(request, str(e))
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_timed_script.html', context)

@login_required
def save_timed_script(request, tdid):
    if not is_contributor(request.user):
        raise PermissionDenied()
    try:
        tr_rec = TutorialResource.objects.get(tutorial_detail_id = tdid, language__name = 'English')
        ContributorRole.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        print e
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    storage_path = tr_rec.tutorial_detail.foss.foss.replace(' ', '-') + '/' + tr_rec.tutorial_detail.level.code + '/' + tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '/' + tr_rec.language.name + '-timed'
    script_path = settings.SCRIPT_URL + storage_path
    form = UploadScriptForm(script_path)
    if request.method == 'POST':
        form = UploadScriptForm(script_path, request.POST)
        if form.is_valid():
            try:
                code = 0
                try:
                    code = urlopen(script_path).code
                except Exception, e:
                    code = e.code
                if(int(code) == 200):
                    tr_rec.timed_script = storage_path
                    tr_rec.save()
                    srt_file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/' + tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-English.vtt'
                    minified_script_url = settings.SCRIPT_URL.strip('/') + '?title=' + quote(storage_path) + '&printable=yes'
                    if generate_subtitle(minified_script_url, srt_file_path):
                        messages.success(request, 'Timed script updated and subtitle file generated successfully!')
                    else:
                        messages.success(request, 'Timed script updated successfully! But there is a in generating subtitle file.')
                    return HttpResponseRedirect('/creation/upload/timed-script/')
                else:
                    messages.error(request, 'Please update the timed-script to wiki before pressing the submit button.')
            except Exception, e:
                messages.error(request, str(e))
    context = {
        'form': form,
        'page_heading': 'timed',
        'script_path': script_path,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/save_timed_script.html', context)

@csrf_exempt
def ajax_upload_timed_script(request):
    data = ''
    foss = request.POST.get('foss', '')
    if foss:
        rows = TutorialDetail.objects.filter(id__in = TutorialResource.objects.filter(tutorial_detail__foss_id = foss, language__name = 'English', script_status = 4).values_list('tutorial_detail_id')).order_by('order')
        data = '<option value="">Select Tutorial Name</option>'
        for row in rows:
            data += '<option value="' + str(row.id) + '">' + row.tutorial + '</option>'
    return HttpResponse(json.dumps(data), content_type='application/json')


@login_required
def upload_prerequisite(request, trid):
    tr_rec = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        ContributorRole.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        raise PermissionDenied()
    if tr_rec.common_content.prerequisite_status > 2 and tr_rec.common_content.prerequisite_status != 5:
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    warning_msg = ''
    if request.method == 'POST':
        form = UploadPrerequisiteForm(request.user, request.POST)
        if form.is_valid():
            try:
                prev_state = tr_rec.common_content.prerequisite_status
                if tr_rec.common_content.prerequisite_id != request.POST['tutorial_name']:
                    tr_rec.common_content.prerequisite_id = request.POST['tutorial_name']
                else:
                    warning_msg = 'There is no change in Prerequisite'
                tr_rec.common_content.prerequisite_user = request.user
                tr_rec.common_content.prerequisite_status = 2
                tr_rec.common_content.save()
                ContributorLog.objects.create(status = prev_state, user = request.user, tutorial_resource = tr_rec, component = 'prerequisite')
                comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
                add_domainreviewer_notification(tr_rec, comp_title, 'Prerequisite waiting for Domain review')
                response_msg = 'Prerequisite status updated successfully!'
            except Exception, e:
                error_msg = 'Something went wrong, please try again later.'
        else:
            context = {
                'form': form,
            }
            context.update(csrf(request))
            return render(request, 'creation/templates/upload_prerequisite.html', context)
    form = UploadPrerequisiteForm(request.user)
    if response_msg:
        messages.success(request, response_msg)
    if error_msg:
        messages.error(request, error_msg)
    if warning_msg:
        messages.warning(request, warning_msg)
    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_prerequisite.html', context)

@login_required
def upload_keywords(request, trid):
    tr_rec = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        ContributorRole.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        raise PermissionDenied()
    if tr_rec.common_content.keyword_status > 2 and tr_rec.common_content.keyword_status != 5:
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    warning_msg = ''
    if request.method == 'POST':
        form = UploadKeywordsForm(trid, request.POST)
        if form.is_valid():
            try:
                prev_state = tr_rec.common_content.keyword_status
                if tr_rec.common_content.keyword != request.POST['keywords']:
                    tr_rec.common_content.keyword = request.POST['keywords'].lower()
                else:
                    warning_msg = 'There is no change in keywords'
                tr_rec.common_content.keyword_user = request.user
                tr_rec.common_content.keyword_status = 2
                tr_rec.common_content.save()
                ContributorLog.objects.create(status = prev_state, user = request.user, tutorial_resource = tr_rec, component = 'keyword')
                comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
                add_domainreviewer_notification(tr_rec, comp_title, 'Keywords waiting for Domain review')
                response_msg = 'Keywords status updated successfully!'
            except Exception, e:
                error_msg = 'Something went wrong, please try again later.'
        else:
            context = {
                'form': form,
            }
            context.update(csrf(request))
            return render(request, 'creation/templates/upload_keywords.html', context)
    form = UploadKeywordsForm(trid)
    if response_msg:
        messages.success(request, response_msg)
    if error_msg:
        messages.error(request, error_msg)
    if warning_msg:
        messages.warning(request, warning_msg)
    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_keywords.html', context)


@login_required
def upload_component(request, trid, component):
    tr_rec = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        ContributorRole.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
        comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
        contrib_log = ContributorLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_log = NeedImprovementLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
    except Exception, e:
        raise PermissionDenied()
    if (component == 'video' or component == 'audio') and getattr(tr_rec, 'video' + '_status') == 4:
        raise PermissionDenied()
    elif (component == 'slide' or component == 'code' or component == 'assignment') and getattr(tr_rec.common_content, component + '_status') == 4:
        raise PermissionDenied()
    else:
        if request.method == 'POST':
            response_msg = ''
            error_msg = ''
	    
            form = ComponentForm(component, request.POST, request.FILES)
            if form.is_valid():
                try:
                    comp_log = ContributorLog()
                    comp_log.user = request.user
                    comp_log.tutorial_resource = tr_rec
                    comp_log.component = component
                    if component == "audio":
                        file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                        file_name =  tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-' + tr_rec.language.name + file_extension
                        file_path = settings.MEDIA_ROOT + 'temp/'
                        t = subprocess.Popen(["mkdir","-p",file_path])
                        full_path = file_path + file_name
                        if os.path.isfile(full_path):
                            p=subprocess.Popen(["rm","-rf",full_path,full_path[:-4]+"-nonoise.ogg"])
                            while p.poll() == None:
                                pass
                        fout = open(full_path, 'wb+')
                        f = request.FILES['comp']
                        for chunk in f.chunks():
                            fout.write(chunk)
                        fout.close()
                        tr_rec.audio = file_name
                        tr_rec.video = tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Video' + '.webm'
                        tr_rec.video_user = request.user
                        tr_rec.video_status = 0
                        if not tr_rec.version:
                            tr_rec.version = 1
                        tr_rec.save()
                        subprocess.Popen(["python",settings.BASE_DIR+"/creation/sox.py",full_path])	
                        response_msg = component+' uploaded successfully!'
                    elif component == 'video':
                        file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                        file_name = tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Video' + file_extension
                        file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/'
                        full_path = file_path + file_name
                        if os.path.isfile(file_path + tr_rec.video) and tr_rec.video_status > 0:
                            if 'isarchive' in request.POST and int(request.POST.get('isarchive', 0)) > 0:
                                archived_file = 'Archived-' + str(request.user.id) + '-' + str(int(time.time())) + '-' + tr_rec.video
                                os.rename(file_path + tr_rec.video, file_path + archived_file)
                                ArchivedVideo.objects.create(tutorial_resource = tr_rec, user = request.user, version = tr_rec.version, video = archived_file, atype = tr_rec.video_status)
                                if int(request.POST.get('isarchive', 0)) == 2:
                                    tr_rec.version += 1
                        fout = open(full_path, 'wb+')
                        f = request.FILES['comp']
                        # Iterate through the chunks.
                        for chunk in f.chunks():
                            fout.write(chunk)
                        fout.close()
                        if os.path.isfile(full_path[0:-4]+".webm"):
                           subprocess.Popen(["rm",full_path[0:-4]+".webm"])
                        subprocess.Popen(["/usr/bin/ffmpeg","-y","-i",full_path,"-vcodec","libvpx","-af","volume=0.0","-max_muxing_queue_size","1024","-f","webm",full_path[:-4]+".webm"],stdout=subprocess.PIPE)
                        # subprocess.Popen(["ffmpeg","-i",full_path,"-an",full_path[:-4]+".webm"])
                        if os.path.isfile(full_path[:-9]+tr_rec.language.name+".ogg"):
                            subprocess.Popen(["rm",full_path[:-9]+tr_rec.language.name+".ogg"])
                        subprocess.Popen(["/usr/bin/ffmpeg","-y","-i",full_path,"-vn","-acodec","libvorbis",full_path[:-9]+tr_rec.language.name+".ogg"])
                        # subprocess.Popen(["ffmpeg","-i",full_path,"-vn",full_path[:-9]+tr_rec.language.name+".ogg"])
                        comp_log.status = tr_rec.video_status
                        tr_rec.video = file_name[:-4]+".webm"
                        tr_rec.audio = tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-' + 'English' + '.ogg'
                        tr_rec.video_user = request.user
                        tr_rec.video_status = 1
                        if not tr_rec.version:
                            tr_rec.version = 1
                        tr_rec.video_thumbnail_time = '00:' + request.POST.get('thumb_mins', '00') + ':' + request.POST.get('thumb_secs', '00')
    	                tr_rec.save()
    	                if tr_rec.language.name == 'English':
    	                    create_thumbnail(tr_rec, 'Big', tr_rec.video_thumbnail_time, '700:500')
                            create_thumbnail(tr_rec, 'Small', tr_rec.video_thumbnail_time,'170:127')
                        comp_log.save()
    	                comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
                        add_adminreviewer_notification(tr_rec, comp_title, component+' waiting for admin review')
                        response_msg = component+' uploaded successfully!'
                    elif component == 'slide':
                        file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                        file_name =  tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Slides' + file_extension
                        file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/resources/' + file_name
                        fout = open(file_path, 'wb+')
                        f = request.FILES['comp']
                        for chunk in f.chunks():
                            fout.write(chunk)
                        fout.close()
                        comp_log.status = tr_rec.common_content.slide_status
                        tr_rec.common_content.slide = file_name
                        tr_rec.common_content.slide_status = 2
                        tr_rec.common_content.slide_user = request.user
                        tr_rec.common_content.save()
                        comp_log.save()
                        add_domainreviewer_notification(tr_rec, comp_title, component.title() + ' waiting for domain review')
                        response_msg = 'Slides uploaded successfully!'
                    elif component == 'code':
                        file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                        file_name =  tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Codefiles' + file_extension
                        file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/resources/' + file_name
                        fout = open(file_path, 'wb+')
                        f = request.FILES['comp']
                        # Iterate through the chunks.
                        for chunk in f.chunks():
                            fout.write(chunk)
                        fout.close()
                        comp_log.status = tr_rec.common_content.code_status
                        tr_rec.common_content.code = file_name
                        tr_rec.common_content.code_status = 2
                        tr_rec.common_content.code_user = request.user
                        tr_rec.common_content.save()
                        comp_log.save()
                        add_domainreviewer_notification(tr_rec, comp_title, component.title() + ' waiting for domain review')
                        response_msg = 'Code files uploaded successfully!'
                    elif component == 'assignment':
                        file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                        file_name =  tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Assignment' + file_extension
                        file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/resources/' + file_name
                        fout = open(file_path, 'wb+')
                        f = request.FILES['comp']
                        # Iterate through the chunks.
                        for chunk in f.chunks():
                            fout.write(chunk)
                        fout.close()
                        comp_log.status = tr_rec.common_content.assignment_status
                        tr_rec.common_content.assignment = file_name
                        tr_rec.common_content.assignment_status = 2
                        tr_rec.common_content.assignment_user = request.user
                        tr_rec.common_content.save()
                        comp_log.save()
                        add_domainreviewer_notification(tr_rec, comp_title, component.title() + ' waiting for domain review')
                        response_msg = 'Assignment file uploaded successfully!'
                    elif component == 'additional_material':
                        file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                        file_name =  tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Additionalmaterial' + file_extension
                        file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/resources/' + file_name
                        fout = open(file_path, 'wb+')
                        f = request.FILES['comp']
                        # Iterate through the chunks.
                        for chunk in f.chunks():
                            fout.write(chunk)
                        fout.close()
                        comp_log.status = tr_rec.common_content.assignment_status
                        tr_rec.common_content.additional_material = file_name
                        tr_rec.common_content.additional_material_status = 2
                        tr_rec.common_content.additional_material_user = request.user
                        tr_rec.common_content.save()
                        comp_log.save()
                        add_domainreviewer_notification(
                            tr_rec, comp_title,
                            '{} waiting for domain review'.format(component.replace('_', ' ').title()))
                        response_msg = 'Additional material uploaded successfully!'
                except Exception, e:
                    print e
                    error_msg = 'Something went wrong, please try again later.'
                form = ComponentForm(component)
                if response_msg:
                    messages.success(request, response_msg)
                if error_msg:
                    messages.error(request, error_msg)
                context = {
                    'form': form,
                    'tr': tr_rec,
                    'title': component.replace('_', ' '),
                }
                context.update(csrf(request))
                return render(request, 'creation/templates/upload_component.html', context)
            else:
                context = {
                    'form': form,
                    'tr': tr_rec,
                    'title': component.replace('_', ' '),
                }
                context.update(csrf(request))
                return render(request, 'creation/templates/upload_component.html', context)
    form = ComponentForm(component)
    context = {
        'form': form,
        'tr': tr_rec,
        'title': component.replace('_', ' '),
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_component.html', context)

@login_required
def mark_notrequired(request, trid, tcid, component):
    tcc = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        ContributorRole.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        raise PermissionDenied()
    try:
        tcc = TutorialCommonContent.objects.get(pk = tcid)
        if getattr(tcc, component + '_status') == 0:
            prev_state = getattr(tcc, component + '_status')
            setattr(tcc, component + '_status', 6)
            setattr(tcc, component + '_user_id', request.user.id)
            tcc.save()
            ContributorLog.objects.create(user = request.user, tutorial_resource_id = trid, component = component, status = prev_state)
            messages.success(request, component.title() + " status updated successfully!")
        else:
            messages.error(request, "Invalid resource id!")
    except Exception, e:
        messages.error(request, 'Something went wrong, please try after some time.')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def preview_check_avaiable(request, trid, component):
    '''
    When Audio / Video is uploaded, the frontend needs to check if 
    the preview is ready, this function is called by the `upload_component`
    and a response of `done` and `not-done` is send accordingly.
    '''
    tr_rec = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid)
    except Exception, e:
        print e
        raise PermissionDenied()
    if component == 'video':
        video_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
        audio_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.audio
        video_info = get_video_info(video_path)
        audio_info = get_audio_info(audio_path)
        if video_info['duration'] != 0 and video_info['size'] != 0 and audio_info['duration'] != 0 and audio_info['size'] != 0:
            return HttpResponse("done") 
        return HttpResponse("not-done")
    if component == 'audio':
        audio_path = settings.MEDIA_ROOT + "temp/" + tr_rec.video[:-10]+tr_rec.language.name+"-nonoise.ogg"
        audio_info = get_audio_info(audio_path)
        if audio_info['duration'] != 0 and audio_info['size'] != 0:
            return HttpResponse("done") 
        return HttpResponse("not-done")


def view_component(request, trid, component):
    tr_rec = None
    context = {}
    try:
        tr_rec = TutorialResource.objects.get(pk = trid)
    except Exception, e:
        print e
        raise PermissionDenied()
    if component == 'outline':
        context = {
            'component': component,
            'component_data': tr_rec.outline
        }
    elif component == 'keyword':
        context = {
            'component': component,
            'component_data': tr_rec.common_content.keyword
        }
    elif component == 'video' or component == 'audio':
        video_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
        audio_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.audio
        eng_audio_path = False
        if tr_rec.language.name != "English":
            # If audio is not english `eng_audio_path` will 
            # keep information of the english audio file for 
            # comparision with the audio file of the other language.
            eng_audio_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.audio.rsplit(tr_rec.language.name)[0] + "English.ogg"
        video_info = get_video_info(video_path)
        audio_info = get_audio_info(audio_path)
        eng_audio_info = get_audio_info(eng_audio_path) 
        video_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
        video_info = get_video_info(video_path)
        aud_present = 1
        if os.path.isfile(audio_path) == False:
            aud_present = 0
            messages.error(request,"No File Present")
        context = {
            'tr': tr_rec,
	        'video_mod':tr_rec.video[:-4].replace("-","_")+"_nonoise",
	        'original': tr_rec.video[:-4].replace("-","_"),
            'component': component,
            'video_info': video_info,
            'eng_audio_info': eng_audio_info,
            'audio_info': audio_info,
            'media_url': settings.MEDIA_URL,
            'aud_present': aud_present
        }
    else:
        messages.error(request, 'Invalid component passed as argument!')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return render(request, 'creation/templates/view_component.html', context)


def view_component_audtype(request, trid, component, aud_type):
    tr_rec = None
    context = {}
    try:
        tr_rec = TutorialResource.objects.get(pk = trid)
    except Exception, e:
        print e
        raise PermissionDenied()
    if component == 'outline':
        context = {
            'component': component,
            'component_data': tr_rec.outline
        }
    elif component == 'keyword':
        context = {
            'component': component,
            'component_data': tr_rec.common_content.keyword
        }
    elif component == 'video' or component == 'audio':
        video_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
        
        if aud_type == 'o':
            audio_path = settings.MEDIA_ROOT + "temp/" + tr_rec.audio
        elif aud_type == 'f':
            audio_path = settings.MEDIA_ROOT + "temp/" + tr_rec.audio[:-4] + "-nonoise.ogg"
        else:
            print "test"
            file_name =  aud_type.replace('_', '-') +".ogg"
            file_path_src = settings.MEDIA_ROOT + 'temp/'
            full_path_src = file_path_src + file_name
            file_path_dest = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/'
            if "nonoise" in file_name:
                file_name = file_name[:-12] + ".ogg"
            full_path_dest = file_path_dest + file_name
            subprocess.Popen(["mv",full_path_src,full_path_dest])
            tr_rec.video_status = 1
            tr_rec.audio = file_name
            tr_rec.save()
            messages.success(request, "Your submission has been accepted")
            audio_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.audio
        eng_audio_path = False
        if tr_rec.language.name != "English":
            eng_audio_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.audio.rsplit(tr_rec.language.name)[0] + "English.ogg"
        video_info = get_video_info(video_path)
        audio_info = get_audio_info(audio_path)
        eng_audio_info = get_audio_info(eng_audio_path)
        context = {
            'tr': tr_rec,
            'audio_modified':tr_rec.video[:-10].replace("-","_")+tr_rec.language.name+"_nonoise",
            'audio_original':tr_rec.video[:-10].replace("-","_")+tr_rec.language.name,
            'filtered': tr_rec.video[:-10]+tr_rec.language.name+ "-nonoise", 
            'component': component,
            'video_info': video_info,
            'audio_info': audio_info,
            'media_url': settings.MEDIA_URL,
            'eng_audio_info': eng_audio_info,
            'original': tr_rec.video[:-10]+tr_rec.language.name,
            'aud_type':aud_type,
        }
    else:
        messages.error(request, 'Invalid component passed as argument!')
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return render(request, 'creation/templates/view_component.html', context)

@login_required
def tutorials_contributed(request):
    tmp_ids = []
    if is_contributor(request.user):
        foss_contrib_list = ContributorRole.objects.filter(user = request.user, status = 1)
        for foss_contrib in foss_contrib_list:
            tr_recs = TutorialResource.objects.filter(tutorial_detail__foss_id = foss_contrib.foss_category_id, language_id = foss_contrib.language_id)
            for tr_rec in tr_recs:
                flag = 1
                if tr_rec.language.name == 'English':
                    if (tr_rec.common_content.slide_user_id != request.user.id or tr_rec.common_content.slide_status == 0) and (tr_rec.common_content.code_user_id != request.user.id or tr_rec.common_content.code_status == 0) and (tr_rec.common_content.assignment_user_id != request.user.id or tr_rec.common_content.assignment_status == 0) and (tr_rec.common_content.keyword_user_id != request.user.id or tr_rec.common_content.keyword_status == 0):
                        flag = 0
                else:
                    flag = 0
                if flag == 1 or (tr_rec.outline_user_id == request.user.id and tr_rec.outline_status > 0) or (tr_rec.script_user_id == request.user.id and tr_rec.script_status > 0) or (tr_rec.video_user_id == request.user.id and tr_rec.video_status > 0):
                    tmp_ids.append(tr_rec.id)
        tmp_recs = None
        ordering = ''
        header = ''
        try:
            tmp_recs = TutorialResource.objects.filter(id__in = tmp_ids).distinct()
            raw_get_data = request.GET.get('o', None)
            header = {
                1: SortableHeader('S.No', False),
                2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
                3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
                4: SortableHeader('language__name', True, 'Language'),
                5: SortableHeader('Outline', False, '', 'col-center'),
                6: SortableHeader('Script', False, '', 'col-center'),
                7: SortableHeader('Slide', False, '', 'col-center'),
                8: SortableHeader('Video', False, '', 'col-center'),
                9: SortableHeader('Codefiles', False, '', 'col-center'),
                10: SortableHeader('Assignment', False, '', 'col-center'),
                11: SortableHeader('Additional material', False, '', 'col-center'),
                12: SortableHeader('Prerequisite', False, '', 'col-center'),
                13: SortableHeader('Keywords', False, '', 'col-center'),
                14: SortableHeader('Status', False)
            }
            tmp_recs = get_sorted_list(request, tmp_recs, header, raw_get_data)
            ordering = get_field_index(raw_get_data)
            counter = 1
            for tmp_rec in tmp_recs:
                if tmp_rec.id == 3311:
                    print counter, tmp_rec.tutorial_detail.tutorial
                counter += 1
            page = request.GET.get('page')
            tmp_recs = get_page(tmp_recs, page)
        except:
            pass

        context = {
            'collection': tmp_recs,
            'header': header,
            'ordering': ordering,
            'media_url': settings.MEDIA_URL
        }
        return render(request, 'creation/templates/my_contribs.html', context)
    else:
        raise PermissionDenied()

@login_required
def tutorials_pending(request):
    tmp_ids = []
    if is_contributor(request.user) or is_domainreviewer(request.user) or \
        is_qualityreviewer(request.user) or is_administrator(is_domainreviewer(request.user)):
        try:
            tmp_recs = TutorialResource.objects.filter(status=0)
            raw_get_data = request.GET.get('o', None)
            header = {
                1: SortableHeader('S.No', False),
                2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
                3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
                4: SortableHeader('language__name', True, 'Language'),
                5: SortableHeader('Outline', False, '', 'col-center'),
                6: SortableHeader('Script', False, '', 'col-center'),
                7: SortableHeader('Slide', False, '', 'col-center'),
                8: SortableHeader('Video', False, '', 'col-center'),
                9: SortableHeader('Codefiles', False, '', 'col-center'),
                10: SortableHeader('Assignment', False, '', 'col-center'),
                11: SortableHeader('Additional material', False, '', 'col-center'),
                12: SortableHeader('Prerequisite', False, '', 'col-center'),
                13: SortableHeader('Keywords', False, '', 'col-center'),
                14: SortableHeader('Status', False)
            }
            tmp_recs = get_sorted_list(request, tmp_recs, header, raw_get_data)
            ordering = get_field_index(raw_get_data)
            counter = 1
            for tmp_rec in tmp_recs:
                if tmp_rec.id == 3311:
                    print counter, tmp_rec.tutorial_detail.tutorial
                counter += 1
            page = request.GET.get('page')
            tmp_recs = get_page(tmp_recs, page, 50)
        except Exception, e:
            print e
            pass

        context = {
            'collection': tmp_recs,
            'header': header,
            'ordering': ordering,
            'media_url': settings.MEDIA_URL
        }
        return render(request, 'creation/templates/pending_tutorial.html', context)
    else:
        raise PermissionDenied()

@login_required
def admin_review_index(request):
    if not is_videoreviewer(request.user):
        raise PermissionDenied()
    tr_recs = None
    try:
        collection = TutorialResource.objects.filter(video_status = 1, status = 0)
        header = {
            1: SortableHeader('S.No', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
            3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('script_status', True, 'Script'),
            6: SortableHeader('updated', True, 'Date & Time'),
            7: SortableHeader('Action', False)
        }
        raw_get_data = request.GET.get('o', None)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        context = {
            'collection': collection,
            'header': header,
            'ordering': ordering,
            'script_url': settings.SCRIPT_URL
        }
        return render(request, 'creation/templates/admin_review_index.html', context)
    except Exception, e:
        return e

@login_required
def admin_review_video(request, trid):
    if not is_videoreviewer(request.user):
        raise PermissionDenied()
    try:
        tr = TutorialResource.objects.get(pk = trid, status = 0, video_status = 1)
        tut_title = tr.tutorial_detail.foss.foss + ': ' + tr.tutorial_detail.tutorial + ' - ' + tr.language.name
    except:
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    if request.method == 'POST':
        form = ReviewVideoForm(request.POST)
        if form.is_valid():
            form = ReviewVideoForm()
            if request.POST['video_status'] == '2':
                try:
                    tr.video_status = 2
                    tr.save()
                    AdminReviewLog.objects.create(status = tr.video_status, user = request.user, tutorial_resource = tr)
                    add_contributor_notification(tr, tut_title, 'Video accepted by Admin reviewer')
                    add_domainreviewer_notification(tr, tut_title, 'Video waiting for Domain review')
                    response_msg = 'Review status updated successfully!'
                except Exception as error:
                    print error
                    error_msg = 'Something went wrong, please try again later.'
            elif request.POST['video_status'] == '5':
                try:
                    prev_state = tr.video_status
                    tr.video_status = 5
                    tr.save()
                    NeedImprovementLog.objects.create(user = request.user, tutorial_resource = tr, review_state = prev_state, component = 'video', comment = request.POST['feedback'])
                    AdminReviewLog.objects.create(status = tr.video_status, user = request.user, tutorial_resource = tr)
                    add_contributor_notification(tr, tut_title, 'Video is under Need Improvement state')
                    response_msg = 'Review status updated successfully!'
                except Exception as error:
                    print error
                    error_msg = 'Something went wrong, please try again later.'
            else:
                error_msg = 'Invalid status code!'
    else:
        form = ReviewVideoForm()
    video_path = settings.MEDIA_ROOT + "videos/" + str(tr.tutorial_detail.foss_id) + "/" + str(tr.tutorial_detail_id) + "/" + tr.video
    audio_path = settings.MEDIA_ROOT + "videos/" + str(tr.tutorial_detail.foss_id) + "/" + str(tr.tutorial_detail_id) + "/" + tr.audio
    eng_audio_path = False
    if tr.language.name != "English":
        eng_audio_path = settings.MEDIA_ROOT + "videos/" + str(tr.tutorial_detail.foss_id) + "/" + str(tr.tutorial_detail_id) + "/" + tr.audio.rsplit(tr.language.name)[0] + "English.ogg"
    video_info = get_video_info(video_path)
    audio_info = get_audio_info(audio_path)
    eng_audio_info = get_audio_info(eng_audio_path)
    if error_msg:
        messages.error(request, error_msg)
    if response_msg:
        messages.success(request, response_msg)
    context = {
        'tr': tr,
        'form': form,
        'media_url': settings.MEDIA_URL,
        'video_info': video_info,
        'audio_info': audio_info,
        'eng_audio_info': eng_audio_info,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/admin_review_video.html', context)

@login_required
def admin_reviewed_video(request):
    collection = None
    header = ''
    ordering = ''
    try:
        header = {
            1: SortableHeader('S.No', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
            3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Outline', False, '', 'col-center'),
            6: SortableHeader('Script', False, '', 'col-center'),
            7: SortableHeader('Slide', False, '', 'col-center'),
            8: SortableHeader('Video', False, '', 'col-center'),
            9: SortableHeader('Codefiles', False, '', 'col-center'),
            10: SortableHeader('Assignment', False, '', 'col-center'),
            11: SortableHeader('Additional material', False, '', 'col-center'),
            12: SortableHeader('Prerequisite', False, '', 'col-center'),
            13: SortableHeader('Keywords', False, '', 'col-center'),
            14: SortableHeader('Status', False),
            15: SortableHeader('created', True, 'Date')
        }
        collection = TutorialResource.objects.filter(id__in = AdminReviewLog.objects.filter(user = request.user).values_list('tutorial_resource_id').distinct())
        raw_get_data = request.GET.get('o', None)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        page = request.GET.get('page')
        collection = get_page(collection, page)
    except:
        messages.error('Something went wrong, Please try again later.')
    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/admin_review_reviewed.html', context)

@login_required
def tutorials_needimprovement(request):
    if not is_contributor(request.user):
        raise PermissionDenied()
    tmp_ids = []
    con_roles = ContributorRole.objects.filter(user_id = request.user.id, status = 1)
    for rec in con_roles:
        tr_recs = TutorialResource.objects.filter(tutorial_detail__foss_id = rec.foss_category_id, language_id = rec.language_id, status = 0)
        for tr_rec in tr_recs:
            flag = 1
            if tr_rec.language.name == 'English':
                if tr_rec.common_content.slide_status != 5 and tr_rec.common_content.code_status != 5 and tr_rec.common_content.assignment_status != 5 and tr_rec.common_content.prerequisite_status != 5 and tr_rec.common_content.keyword_status != 5:
                    flag = 0
            else:
                flag = 0
            if flag or tr_rec.outline_status == 5 or tr_rec.script_status == 5 or tr_rec.video_status == 5:
                tmp_ids.append(tr_rec.id)
    tmp_recs = None
    ordering = ''
    header = ''
    try:
        tmp_recs = TutorialResource.objects.filter(id__in = tmp_ids)
        raw_get_data = request.GET.get('o', None)
        header = {
            1: SortableHeader('S.No', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
            3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Outline', False, '', 'col-center'),
            6: SortableHeader('Script', False, '', 'col-center'),
            7: SortableHeader('Slide', False, '', 'col-center'),
            8: SortableHeader('Video', False, '', 'col-center'),
            9: SortableHeader('Codefiles', False, '', 'col-center'),
            10: SortableHeader('Assignment', False, '', 'col-center'),
            11: SortableHeader('Additional material', False, '', 'col-center'),
            12: SortableHeader('Prerequisite', False, '', 'col-center'),
            13: SortableHeader('Keywords', False, '', 'col-center'),
            14: SortableHeader('Status', False)
        }
        tmp_recs = get_sorted_list(request, tmp_recs, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        page = request.GET.get('page')
        tmp_recs = get_page(tmp_recs, page)
    except:
        pass

    context = {
        'collection': tmp_recs,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/my_needimprovements.html', context)

@login_required
def domain_review_index(request):
    if not is_domainreviewer(request.user):
        raise PermissionDenied()
    tmp_ids = []
    dr_roles = DomainReviewerRole.objects.filter(user_id = request.user.id, status = 1)
    for rec in dr_roles:
        tr_recs = TutorialResource.objects.filter(tutorial_detail_id__in = TutorialDetail.objects.filter(foss_id = rec.foss_category_id).values_list('id'), language_id = rec.language_id, status = 0).order_by('updated')
        for tr_rec in tr_recs:
            flag = 1
            if tr_rec.language.name == 'English':
                if tr_rec.common_content.slide_status != 2 and tr_rec.common_content.code_status != 2 and \
                   tr_rec.common_content.assignment_status != 2 and tr_rec.common_content.prerequisite_status != 2 and \
                   tr_rec.common_content.keyword_status != 2 and tr_rec.common_content.additional_material_status != 2:
                    flag = 0
            else:
                flag = 0
            if flag or tr_rec.outline_status == 2 or tr_rec.script_status == 2 or tr_rec.video_status == 2:
                tmp_ids.append(tr_rec.id)
    collection = None
    ordering = ''
    header = ''
    try:
        raw_get_data = request.GET.get('o', None)
        header = {
            1: SortableHeader('S.No', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
            3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Outline', False, '', 'col-center'),
            6: SortableHeader('Script', False, '', 'col-center'),
            7: SortableHeader('Slide', False, '', 'col-center'),
            8: SortableHeader('Video', False, '', 'col-center'),
            9: SortableHeader('Codefiles', False, '', 'col-center'),
            10: SortableHeader('Assignment', False, '', 'col-center'),
            11: SortableHeader('Additional material', False, '', 'col-center'),
            12: SortableHeader('Prerequisite', False, '', 'col-center'),
            13: SortableHeader('Keywords', False, '', 'col-center'),
            14: SortableHeader('<span title="" data-original-title="" class="fa fa-cogs fa-2"></span>', False, '', 'col-center')
        }
        collection = TutorialResource.objects.filter(id__in = tmp_ids)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        page = request.GET.get('page')
        collection = get_page(collection, page)
    except:
        pass
    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/domain_review_index.html', context)

@login_required
def domain_review_tutorial(request, trid):
    if not is_domainreviewer(request.user):
        raise PermissionDenied()
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
    except:
        raise PermissionDenied()
    if DomainReviewerRole.objects.filter(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1).count() == 0:
        raise PermissionDenied()
    try:
        contrib_log = ContributorLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_log = NeedImprovementLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_history = DomainReviewLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
    except:
        contrib_log = None
        review_log = None
        review_history = None
    context = {
        'tr': tr_rec,
        'contrib_log': contrib_log,
        'review_log': review_log,
        'script_base': settings.SCRIPT_URL,
        'review_history': review_history
    }
    return render(request, 'creation/templates/domain_review_tutorial.html', context)

@login_required
def domain_review_component(request, trid, component):
    if not is_domainreviewer(request.user):
        raise PermissionDenied()
    try:
        tr = TutorialResource.objects.get(pk = trid, status = 0)
        comp_title = tr.tutorial_detail.foss.foss + ': ' + tr.tutorial_detail.tutorial + ' - ' + tr.language.name
    except:
        raise PermissionDenied()
    if DomainReviewerRole.objects.filter(user_id = request.user.id, foss_category_id = tr.tutorial_detail.foss_id, language_id = tr.language_id).count() == 0:
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    if request.method == 'POST':
        form = DomainReviewComponentForm(request.POST)
        if form.is_valid():
            if request.POST['component_status'] == '3':
                try:
                    execFlag = 0
                    if component == 'outline' or component == 'script' or component == 'video':
                        setattr(tr, component + '_status', 3)
                        tr.save()
                        execFlag = 1
                    else:
                        if tr.language.name == 'English':
                            setattr(tr.common_content, component + '_status', 3)
                            tr.common_content.save()
                            execFlag = 1
                    if execFlag:
                        DomainReviewLog.objects.create(status = 3, component = component, user = request.user, tutorial_resource = tr)
                        add_qualityreviewer_notification(tr, comp_title, component.title() + ' waiting for Quality review')
                        add_contributor_notification(tr, comp_title, component.replace('_', ' ').title() + ' accepted by Domain reviewer')
                        response_msg = 'Review status updated successfully!'
                    else:
                        error_msg = 'Something went wrong, please try again later.'
                except Exception, e:
                    print e
                    error_msg = 'Something went wrong, please try again later.'
            elif request.POST['component_status'] == '5':
                try:
                    prev_state = 0
                    if component == 'outline' or component == 'script' or component == 'video':
                        prev_state = getattr(tr, component + '_status')
                        setattr(tr, component + '_status', 5)
                        tr.save()
                    else:
                        prev_state = getattr(tr.common_content, component + '_status')
                        setattr(tr.common_content, component + '_status', 5)
                        tr.common_content.save()
                    NeedImprovementLog.objects.create(user = request.user, tutorial_resource = tr, review_state = prev_state, component = component, comment = request.POST['feedback'])
                    DomainReviewLog.objects.create(status = 5, component = component, user = request.user, tutorial_resource = tr)
                    add_contributor_notification(tr, comp_title, component.title() + ' is under Need Improvement state')
                    response_msg = 'Review status updated successfully!'
                except:
                    error_msg = 'Something went wrong, please try again later.'
            form = DomainReviewComponentForm()
    else:
        form = DomainReviewComponentForm()
    if error_msg:
        messages.error(request, error_msg)
    if response_msg:
        messages.success(request, response_msg)
    context = {
        'form': form,
        'tr': tr,
        'component': component,
    }

    return render(request, 'creation/templates/domain_review_component.html', context)

@login_required
def domain_reviewed_tutorials(request):
    collection = None
    ordering = ''
    header = ''
    try:
        raw_get_data = request.GET.get('o', None)
        header = {
            1: SortableHeader('S.No', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
            3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Outline', False, '', 'col-center'),
            6: SortableHeader('Script', False, '', 'col-center'),
            7: SortableHeader('Slide', False, '', 'col-center'),
            8: SortableHeader('Video', False, '', 'col-center'),
            9: SortableHeader('Codefiles', False, '', 'col-center'),
            10: SortableHeader('Assignment', False, '', 'col-center'),
            11: SortableHeader('Additional material', False, '', 'col-center'),
            12: SortableHeader('Prerequisite', False, '', 'col-center'),
            13: SortableHeader('Keywords', False, '', 'col-center'),
            14: SortableHeader('Status', False, '', 'col-center'),
            15: SortableHeader('created', True, 'Date')
        }
        collection = TutorialResource.objects.filter(id__in = DomainReviewLog.objects.filter(user = request.user).values_list('tutorial_resource_id').distinct())
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        page = request.GET.get('page')
        collection = get_page(collection, page)
    except:
        messages.error('Something went wrong, Please try again later.')
    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/domain_review_reviewed.html', context)

def accept_all(request, review, trid):
    status_flag = {
        'domain': 3,
        'quality': 4
    }
    flag = 0
    reviewer_role_check = None
    if review == 'domain':
        reviewer_role_check = DomainReviewerRole
        if not is_domainreviewer(request.user):
            raise PermissionDenied()
    else:
        reviewer_role_check = QualityReviewerRole
        if not is_qualityreviewer(request.user):
            raise PermissionDenied()
    try:
        tr = TutorialResource.objects.get(pk = trid, status = 0)
        comp_title = tr.tutorial_detail.foss.foss + ': ' + tr.tutorial_detail.tutorial + ' - ' + tr.language.name
    except:
        raise PermissionDenied()
    if reviewer_role_check and reviewer_role_check.objects.filter(user_id = request.user.id, foss_category_id = tr.tutorial_detail.foss_id, language_id = tr.language_id).count() == 0:
        raise PermissionDenied()
    if review in status_flag:
        current_status = status_flag[review] - 1
    else:
        raise PermissionDenied()
    comp_message = ''
    if tr.outline_status > 0 and tr.outline_status == current_status:
        tr.outline_status = status_flag[review]
        if review == 'quality':
            QualityReviewLog.objects.create(status = status_flag[review], component = 'outline', user = request.user, tutorial_resource = tr)
            comp_message = 'Outline accepted by Quality reviewer'
        else:
            DomainReviewLog.objects.create(status = status_flag[review], component = 'outline', user = request.user, tutorial_resource = tr)
            add_qualityreviewer_notification(tr, comp_title, 'Outline waiting for Quality review')
            comp_message = 'Outline accepted by Domain reviewer'
        add_contributor_notification(tr, comp_title, comp_message)
        flag = 1

    if tr.script_status > 0 and tr.script_status == current_status:
        tr.script_status = status_flag[review]
        if review == 'quality':
            QualityReviewLog.objects.create(status = status_flag[review], component = 'script', user = request.user, tutorial_resource = tr)
            comp_message = 'Script accepted by Quality reviewer'
        else:
            DomainReviewLog.objects.create(status = status_flag[review], component = 'script', user = request.user, tutorial_resource = tr)
            add_qualityreviewer_notification(tr, comp_title, 'Script waiting for Quality review')
            comp_message = 'Script accepted by Domain reviewer'
        add_contributor_notification(tr, comp_title, comp_message)
        flag = 1

    if tr.video_status > 0 and tr.video_status == current_status:
        tr.video_status = status_flag[review]
        if review == 'quality':
            QualityReviewLog.objects.create(status = status_flag[review], component = 'video', user = request.user, tutorial_resource = tr)
            comp_message = 'Video accepted by Quality reviewer'
        else:
            DomainReviewLog.objects.create(status = status_flag[review], component = 'video', user = request.user, tutorial_resource = tr)
            add_qualityreviewer_notification(tr, comp_title, 'Video waiting for Quality review')
            comp_message = 'Video accepted by Domain reviewer'
        add_contributor_notification(tr, comp_title, comp_message)
        flag = 1
    tr.save()

    if tr.language.name == 'English':
        if tr.common_content.slide_status > 0 and tr.common_content.slide_status == current_status:
            tr.common_content.slide_status = status_flag[review]
            if review == 'quality':
                QualityReviewLog.objects.create(status = status_flag[review], component = 'slide', user = request.user, tutorial_resource = tr)
                comp_message = 'Slide accepted by Quality reviewer'
            else:
                DomainReviewLog.objects.create(status = status_flag[review], component = 'slide', user = request.user, tutorial_resource = tr)
                add_qualityreviewer_notification(tr, comp_title, 'Slide waiting for Quality review')
                comp_message = 'Slide accepted by Domain reviewer'
            add_contributor_notification(tr, comp_title, comp_message)
            flag = 1

        if tr.common_content.code_status > 0 and tr.common_content.code_status == current_status:
            tr.common_content.code_status = status_flag[review]
            if review == 'quality':
                QualityReviewLog.objects.create(status = status_flag[review], component = 'code', user = request.user, tutorial_resource = tr)
                comp_message = 'Codefiles accepted by Quality reviewer'
            else:
                DomainReviewLog.objects.create(status = status_flag[review], component = 'code', user = request.user, tutorial_resource = tr)
                add_qualityreviewer_notification(tr, comp_title, 'Codefiles waiting for Quality review')
                comp_message = 'Codefiles accepted by Domain reviewer'
            add_contributor_notification(tr, comp_title, comp_message)
            flag = 1

        if tr.common_content.assignment_status > 0 and tr.common_content.assignment_status == current_status:
            tr.common_content.assignment_status = status_flag[review]
            if review == 'quality':
                QualityReviewLog.objects.create(status = status_flag[review], component = 'assignment', user = request.user, tutorial_resource = tr)
                comp_message = 'Assignment accepted by Quality reviewer'
            else:
                DomainReviewLog.objects.create(status = status_flag[review], component = 'assignment', user = request.user, tutorial_resource = tr)
                add_qualityreviewer_notification(tr, comp_title, 'Assignment waiting for Quality review')
                comp_message = 'Assignment accepted by Domain reviewer'
            add_contributor_notification(tr, comp_title, comp_message)
            flag = 1

        if tr.common_content.additional_material_status > 0 and tr.common_content.additional_material_status == current_status:
            tr.common_content.additional_material_status = status_flag[review]
            if review == 'quality':
                QualityReviewLog.objects.create(status = status_flag[review], component = 'additional_material',
                                                user = request.user, tutorial_resource = tr)
                comp_message = 'Additional material accepted by Quality reviewer'
            else:
                DomainReviewLog.objects.create(status = status_flag[review], component = 'additional_material',
                                               user = request.user, tutorial_resource = tr)
                add_qualityreviewer_notification(tr, comp_title, 'Additional material waiting for Quality review')
                comp_message = 'Additional material accepted by Domain reviewer'
            add_contributor_notification(tr, comp_title, comp_message)
            flag = 1

        if tr.common_content.prerequisite_status > 0 and tr.common_content.prerequisite_status == current_status:
            tr.common_content.prerequisite_status = status_flag[review]
            if review == 'quality':
                QualityReviewLog.objects.create(status = status_flag[review], component = 'prerequisite', user = request.user, tutorial_resource = tr)
                comp_message = 'Prerequisite accepted by Quality reviewer'
            else:
                DomainReviewLog.objects.create(status = status_flag[review], component = 'prerequisite', user = request.user, tutorial_resource = tr)
                add_qualityreviewer_notification(tr, comp_title, 'Prerequisite waiting for Quality review')
                comp_message = 'Prerequisite accepted by Domain reviewer'
            add_contributor_notification(tr, comp_title, comp_message)
            flag = 1

        if tr.common_content.keyword_status > 0 and tr.common_content.keyword_status == current_status:
            tr.common_content.keyword_status = status_flag[review]
            if review == 'quality':
                QualityReviewLog.objects.create(status = status_flag[review], component = 'keyword', user = request.user, tutorial_resource = tr)
                comp_message = 'Keywords accepted by Quality reviewer'
            else:
                DomainReviewLog.objects.create(status = status_flag[review], component = 'keyword', user = request.user, tutorial_resource = tr)
                add_qualityreviewer_notification(tr, comp_title, 'Keywords waiting for Quality review')
                comp_message = 'Keywords accepted by Domain reviewer'
            add_contributor_notification(tr, comp_title, comp_message)
            flag = 1

        tr.common_content.save()
    if not flag:
        messages.warning(request, 'There is no component available for Domain reviewer to accept.')

    return HttpResponseRedirect('/creation/' + review + '-review/tutorial/' + str(tr.id) + '/')

@login_required
def quality_review_index(request):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tmp_ids = []
    qr_roles =  QualityReviewerRole.objects.filter(user_id = request.user.id, status = 1)
    for rec in qr_roles:
        if rec.language.name == 'English':
            tr_recs = TutorialResource.objects.filter(Q(outline_status = 3) | Q(script_status = 3) | Q(video_status = 3) | Q(common_content__slide_status = 3) | Q(common_content__code_status = 3) | Q(common_content__assignment_status = 3) | Q(common_content__keyword_status = 3) | Q(common_content__prerequisite_status = 3) | Q(common_content__additional_material_status = 3), Q(tutorial_detail__foss_id = rec.foss_category_id) & Q(language_id = rec.language_id) & Q(status = 0))
        else:
            tr_recs = TutorialResource.objects.filter(Q(outline_status=3)|Q(script_status=3)|Q(video_status=3), Q(tutorial_detail__foss_id = rec.foss_category_id) & Q(language_id = rec.language_id) & Q(status = 0)).order_by('updated')

        for tr_rec in tr_recs:
            tmp_ids.append(tr_rec.id)

    collection = None
    header = ''
    ordering = ''
    try:
        raw_get_data = request.GET.get('o', None)
        header = {
            1: SortableHeader('S.No', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
            3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Outline', False, '', 'col-center'),
            6: SortableHeader('Script', False, '', 'col-center'),
            7: SortableHeader('Slide', False, '', 'col-center'),
            8: SortableHeader('Video', False, '', 'col-center'),
            9: SortableHeader('Codefiles', False, '', 'col-center'),
            10: SortableHeader('Assignment', False, '', 'col-center'),
            11: SortableHeader('Additional material', False, '', 'col-center'),
            12: SortableHeader('Prerequisite', False, '', 'col-center'),
            13: SortableHeader('Keywords', False, '', 'col-center'),
            14: SortableHeader('<span title="" data-original-title="" class="fa fa-cogs fa-2"></span>', False, '', 'col-center')
        }
        collection = TutorialResource.objects.filter(id__in = tmp_ids)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        page = request.GET.get('page')
        collection = get_page(collection, page)
    except:
        pass

    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/quality_review_index.html', context)

def publish_tutorial_index(request):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tmp_ids = []
    qr_roles =  QualityReviewerRole.objects.filter(user_id = request.user.id, status = 1)
    for rec in qr_roles:
        if rec.language.name == 'English':
            tr_recs = TutorialResource.objects.filter(Q(common_content__code_status = 4) | Q(common_content__code_status = 6), Q(common_content__assignment_status = 4) | Q(common_content__assignment_status = 6), Q(common_content__prerequisite_status = 4) | Q(common_content__prerequisite_status = 6), Q(outline_status = 4) & Q(script_status = 4) & Q(video_status = 4) & Q(common_content__slide_status = 4) & Q(common_content__keyword_status = 4) & Q(tutorial_detail__foss_id = rec.foss_category_id) & Q(language_id = rec.language_id) & Q(status = 0))
        else:
            tr_recs = TutorialResource.objects.filter(Q(outline_status = 4) & Q(script_status = 4) & Q(video_status = 4) & Q(tutorial_detail__foss_id = rec.foss_category_id) & Q(language_id = rec.language_id) & Q(status = 0)).order_by('updated')

        for tr_rec in tr_recs:
            tmp_ids.append(tr_rec.id)

    collection = None
    header = ''
    ordering = ''
    try:
        raw_get_data = request.GET.get('o', None)
        header = {
            1: SortableHeader('S.No', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
            3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Outline', False, '', 'col-center'),
            6: SortableHeader('Script', False, '', 'col-center'),
            7: SortableHeader('Slide', False, '', 'col-center'),
            8: SortableHeader('Video', False, '', 'col-center'),
            9: SortableHeader('Codefiles', False, '', 'col-center'),
            10: SortableHeader('Assignment', False, '', 'col-center'),
            11: SortableHeader('Additional material', False, '', 'col-center'),
            12: SortableHeader('Prerequisite', False, '', 'col-center'),
            13: SortableHeader('Keywords', False, '', 'col-center'),
            14: SortableHeader('<span title="" data-original-title="" class="fa fa-cogs fa-2"></span>', False, '', 'col-center')
        }
        collection = TutorialResource.objects.filter(id__in = tmp_ids)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        page = request.GET.get('page')
        collection = get_page(collection, page)
    except:
        pass

    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/publish_tutorial_index.html', context)

def public_review_tutorial_index(request):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tmp_ids = []
    qr_roles =  QualityReviewerRole.objects.filter(user_id = request.user.id, status = 1)
    tr_recs = ''
    for rec in qr_roles:
        if rec.language.name != 'English':
            tr_recs = TutorialResource.objects.filter(Q(outline_status__gt = 0) & Q(outline_status__lt = 5), Q(script_status__gt = 0) & Q(script_status__lt = 5), Q(video_status__gt = 0) & Q(video_status__lt = 5), Q(tutorial_detail__foss_id = rec.foss_category_id) & Q(language_id = rec.language_id) & Q(status = 0)).order_by('updated')

        for tr_rec in tr_recs:
            tmp_ids.append(tr_rec.id)

    collection = None
    header = ''
    ordering = ''
    try:
        if len(tmp_ids):
            raw_get_data = request.GET.get('o', None)
            header = {
                1: SortableHeader('S.No', False),
                2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
                3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
                4: SortableHeader('language__name', True, 'Language'),
                5: SortableHeader('Outline', False, '', 'col-center'),
                6: SortableHeader('Script', False, '', 'col-center'),
                7: SortableHeader('Slide', False, '', 'col-center'),
                8: SortableHeader('Video', False, '', 'col-center'),
                9: SortableHeader('Codefiles', False, '', 'col-center'),
                10: SortableHeader('Assignment', False, '', 'col-center'),
                11: SortableHeader('Additional material', False, '', 'col-center'),
                12: SortableHeader('Prerequisite', False, '', 'col-center'),
                13: SortableHeader('Keywords', False, '', 'col-center'),
                14: SortableHeader('<span title="" data-original-title="" class="fa fa-cogs fa-2"></span>', False, '', 'col-center')
            }
            collection = TutorialResource.objects.filter(id__in = tmp_ids)
            collection = get_sorted_list(request, collection, header, raw_get_data)
            ordering = get_field_index(raw_get_data)
            page = request.GET.get('page')
            collection = get_page(collection, page)
    except:
        pass

    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/public_review_tutorial_index.html', context)

@login_required
def public_review_list(request):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tmp_ids = []
    qr_roles =  QualityReviewerRole.objects.filter(user_id = request.user.id, status = 1)
    for rec in qr_roles:
        tr_recs = TutorialResource.objects.filter(tutorial_detail__foss_id = rec.foss_category_id, language_id = rec.language_id, status = 2).order_by('updated')
        for tr_rec in tr_recs:
            tmp_ids.append(tr_rec.id)
    collection = None
    header = ''
    ordering = ''
    try:
        if len(tmp_ids):
            raw_get_data = request.GET.get('o', None)
            header = {
                1: SortableHeader('S.No', False),
                2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
                3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
                4: SortableHeader('language__name', True, 'Language'),
                5: SortableHeader('Outline', False, '', 'col-center'),
                6: SortableHeader('Script', False, '', 'col-center'),
                7: SortableHeader('Slide', False, '', 'col-center'),
                8: SortableHeader('Video', False, '', 'col-center'),
                9: SortableHeader('Codefiles', False, '', 'col-center'),
                10: SortableHeader('Assignment', False, '', 'col-center'),
                11: SortableHeader('Additional material', False, '', 'col-center'),
                12: SortableHeader('Prerequisite', False, '', 'col-center'),
                13: SortableHeader('Keywords', False, '', 'col-center'),
                14: SortableHeader('<span title="" data-original-title="" class="fa fa-cogs fa-2"></span>', False, '', 'col-center', 'colspan=2')
            }
            collection = TutorialResource.objects.filter(id__in = tmp_ids)
            collection = get_sorted_list(request, collection, header, raw_get_data)
            ordering = get_field_index(raw_get_data)
            page = request.GET.get('page')
            collection = get_page(collection, page)
    except:
        pass

    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/public_review_list.html', context)

@login_required
def public_review_publish(request, trid):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 2)
        comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
    except:
        raise PermissionDenied()
    if QualityReviewerRole.objects.filter(user = request.user, foss_category = tr_rec.tutorial_detail.foss).count() == 0:
        raise PermissionDenied()
    flag = 1
    if tr_rec.language.name == 'English':
        if tr_rec.common_content.slide_status > 0 and tr_rec.common_content.code_status > 0 and tr_rec.common_content.assignment_status > 0 and tr_rec.common_content.prerequisite_status > 0 and tr_rec.common_content.keyword_status > 0:
            if tr_rec.common_content.slide_status != 6:
                tr_rec.common_content.slide_status = 4
            if tr_rec.common_content.code_status != 6:
                tr_rec.common_content.code_status = 4
            if tr_rec.common_content.assignment_status != 6:
                tr_rec.common_content.assignment_status = 4
            if tr_rec.common_content.prerequisite_status != 6:
                tr_rec.common_content.prerequisite_status = 4
            tr_rec.common_content.keyword_status = 4
        else:
            flag = 0
    if flag and tr_rec.outline_status > 0 and tr_rec.script_status > 0 and tr_rec.video_status > 0:
        tr_rec.outline_status = 4
        tr_rec.script_status = 4
        tr_rec.video_status = 4
    else:
        flag = 0
    if flag:
        if tr_rec.language.name == 'English':
            tr_rec.common_content.save()
        tr_rec.status = 1
        tr_rec.save()
        add_contributor_notification(tr_rec, comp_title, 'This tutorial is published now.')
        messages.success(request, 'Selected tutorial published successfully!')
    else:
        messages.error('Some components are missing, upload those missing components to publish')
    return HttpResponseRedirect('/creation/public-review/list/')

@login_required
def public_review_mark_as_pending(request, trid):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 2)
        comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
    except:
        raise PermissionDenied()
    if QualityReviewerRole.objects.filter(user = request.user, foss_category = tr_rec.tutorial_detail.foss).count() == 0:
        raise PermissionDenied()
    if tr_rec.language.name == 'English':
        if tr_rec.common_content.slide_status > 0 and tr_rec.common_content.slide_status != 6:
            tr_rec.common_content.slide_status = 2
        if tr_rec.common_content.code_status > 0 and tr_rec.common_content.code_status != 6:
            tr_rec.common_content.code_status = 4
        if tr_rec.common_content.assignment_status > 0 and tr_rec.common_content.assignment_status != 6:
            tr_rec.common_content.assignment_status = 4
        if tr_rec.common_content.prerequisite_status > 0 and tr_rec.common_content.prerequisite_status != 6:
            tr_rec.common_content.prerequisite_status = 4
        if tr_rec.common_content.keyword_status > 0:
            tr_rec.common_content.keyword_status = 2
    if tr_rec.outline_status > 0:
        tr_rec.outline_status = 2
    if tr_rec.script_status > 0:
        tr_rec.script_status = 2
    if tr_rec.video_status > 0:
        tr_rec.video_status = 2
    try:
        tr_rec.common_content.save()
        tr_rec.status = 0
        tr_rec.save()
        add_contributor_notification(tr_rec, comp_title, 'This tutorial moved from public review to regular review process.')
        messages.success(request, 'Selected tutorial is marked as pending.')
    except Exception, e:
        messages.error(request, str(e))

    return HttpResponseRedirect('/creation/public-review/list/')

@login_required
def quality_review_tutorial(request, trid):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
    except:
        raise PermissionDenied()
    if QualityReviewerRole.objects.filter(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1).count() == 0:
        raise PermissionDenied()
    try:
        contrib_log = ContributorLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_log = NeedImprovementLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_history = QualityReviewLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
    except:
        contrib_log = None
        review_log = None
        review_history = None
    context = {
        'tr': tr_rec,
        'contrib_log': contrib_log,
        'review_log': review_log,
        'review_history': review_history,
        'script_base': settings.SCRIPT_URL,
    }
    return render(request, 'creation/templates/quality_review_tutorial.html', context)

@login_required
def quality_review_component(request, trid, component):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    try:
        tr = TutorialResource.objects.get(pk = trid, status = 0)
        comp_title = tr.tutorial_detail.foss.foss + ': ' + tr.tutorial_detail.tutorial + ' - ' + tr.language.name
    except:
        raise PermissionDenied()
    if QualityReviewerRole.objects.filter(user_id = request.user.id, foss_category_id = tr.tutorial_detail.foss_id, language_id = tr.language_id, status = 1).count() == 0:
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    if request.method == 'POST':
        form = QualityReviewComponentForm(request.POST)
        if form.is_valid():
            if request.POST['component_status'] == '4':
                try:
                    execFlag = 0
                    if component == 'outline' or component == 'script' or component == 'video':
                        setattr(tr, component + '_status', 4)
                        tr.save()
                        execFlag = 1
                    else:
                        if tr.language.name == 'English':
                            setattr(tr.common_content, component + '_status', 4)
                            tr.common_content.save()
                            execFlag = 1
                    if execFlag:
                        comp_message = component.title() + ' accepted by Quality reviewer'
                        QualityReviewLog.objects.create(status = 4, component = component, user = request.user, tutorial_resource = tr)
                        add_contributor_notification(tr, comp_title, comp_message)
                        response_msg = 'Review status updated successfully!'
                    else:
                        error_msg = 'Something went wrong, please try again later.'
                except Exception, e:
                    error_msg = 'Something went wrong, please try again later.'
            elif request.POST['component_status'] == '5':
                try:
                    prev_state = 0
                    execFlag = 0
                    if component == 'outline' or component == 'script' or component == 'video':
                        prev_state = getattr(tr, component + '_status')
                        setattr(tr, component + '_status', 5)
                        tr.save()
                        execFlag = 1
                    else:
                        if tr.language.name == 'English':
                            prev_state = getattr(tr.common_content, component + '_status')
                            setattr(tr.common_content, component + '_status', 5)
                            tr.common_content.save()
                            execFlag = 1
                    if execFlag:
                        NeedImprovementLog.objects.create(user = request.user, tutorial_resource = tr, review_state = prev_state, component = component, comment = request.POST['feedback'])
                        comp_message = component.title() + ' is under Need Improvement state'
                        QualityReviewLog.objects.create(status = 5, component = component, user = request.user, tutorial_resource = tr)
                        add_contributor_notification(tr, comp_title, comp_message)
                        response_msg = 'Review status updated successfully!'
                    else:
                        error_msg = 'Something went wrong, please try again later.'
                except:
                    error_msg = 'Something went wrong, please try again later.'
            form = QualityReviewComponentForm()
    else:
        form = QualityReviewComponentForm()
    if error_msg:
        messages.error(request, error_msg)
    if response_msg:
        messages.success(request, response_msg)
    context = {
        'form': form,
        'tr': tr,
        'component': component,
        'component_title': component.replace('_', ' ').title(),
    }

    return render(request, 'creation/templates/quality_review_component.html', context)

@login_required
def public_review_tutorial(request, trid):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
    except:
        raise PermissionDenied()
    if QualityReviewerRole.objects.filter(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1).count() == 0:
        raise PermissionDenied()
    if tr_rec.language.name != 'English' and (tr_rec.outline_status > 0 and tr_rec.outline_status != 5) and (tr_rec.script_status > 0 and tr_rec.script_status != 5) and (tr_rec.video_status > 0 and tr_rec.video_status != 5):
        tr_rec.status = 2
        tr_rec.save()
        PublicReviewLog.objects.create(user = request.user, tutorial_resource = tr_rec)
        add_contributor_notification(tr_rec, comp_title, 'This tutorial is now available for Public review')
        messages.success(request, 'The selected tutorial is now available for Public review')
    else:
        messages.error(request, 'The selected tutorial cannot be marked as Public review')
    return HttpResponseRedirect('/creation/public-review/tutorial/index/')

@login_required
def publish_tutorial(request, trid):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
    except:
        raise PermissionDenied()
    if QualityReviewerRole.objects.filter(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1).count() == 0:
        raise PermissionDenied()
    flag = 0
    if tr_rec.language.name == 'English':
        if tr_rec.common_content.slide_status == 4 and (tr_rec.common_content.code_status == 4 or tr_rec.common_content.code_status == 6) and (tr_rec.common_content.assignment_status == 4 or tr_rec.common_content.assignment_status == 6) and tr_rec.common_content.keyword_status == 4 and (tr_rec.common_content.prerequisite_status == 4 or tr_rec.common_content.prerequisite_status == 6) and (tr_rec.common_content.additional_material_status == 4 or tr_rec.common_content.additional_material_status == 6):
            flag = 1
    else:
        flag = 1
    if flag and tr_rec.outline_status == 4 and tr_rec.script_status == 4 and tr_rec.video_status == 4:
        tr_rec.status = 1 
        tr_rec.publish_at = timezone.now()
        tr_rec.save()
        PublishTutorialLog.objects.create(user = request.user, tutorial_resource = tr_rec)

        add_contributor_notification(tr_rec, comp_title, 'This tutorial is published now')
        messages.success(request, 'The selected tutorial is published successfully')
    else:
        messages.error(request, 'The selected tutorial cannot be marked as Public review')
    return HttpResponseRedirect('/creation/quality-review/tutorial/publish/index/')

@login_required
def quality_reviewed_tutorials(request):
    collection = None
    header = ''
    ordering = ''
    try:
        raw_get_data = request.GET.get('o', None)
        header = {
            1: SortableHeader('S.No', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'Foss'),
            3: SortableHeader('tutorial_detail__tutorial', True, 'Tutorial Name'),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Outline', False, '', 'col-center'),
            6: SortableHeader('Script', False, '', 'col-center'),
            7: SortableHeader('Slide', False, '', 'col-center'),
            8: SortableHeader('Video', False, '', 'col-center'),
            9: SortableHeader('Codefiles', False, '', 'col-center'),
            10: SortableHeader('Assignment', False, '', 'col-center'),
            11: SortableHeader('Additional material', False, '', 'col-center'),
            12: SortableHeader('Prerequisite', False, '', 'col-center'),
            13: SortableHeader('Keywords', False, '', 'col-center'),
            14: SortableHeader('Status', False, '', 'col-center'),
            15: SortableHeader('publishtutoriallog__created', True, 'Date')
        }
        collection = TutorialResource.objects.filter(id__in = QualityReviewLog.objects.filter(user = request.user).values_list('tutorial_resource_id').distinct())
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        page = request.GET.get('page')
        collection = get_page(collection, page)
    except:
        messages.error('Something went wrong, Please try again later.')
    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering
    }
    return render(request, 'creation/templates/quality_review_reviewed.html', context)

@login_required
def delete_creation_notification(request, notif_type, notif_id):
    notif_rec = None
    try:
        if notif_type == "contributor":
            notif_rec = ContributorNotification.objects.get(pk = notif_id, user = request.user)
        elif notif_type == "admin":
            notif_rec = AdminReviewerNotification.objects.get(pk = notif_id, user = request.user)
        elif notif_type == "domain":
            notif_rec = DomainReviewerNotification.objects.get(pk = notif_id, user = request.user)
        elif notif_type == "quality":
            notif_rec = QualityReviewerNotification.objects.get(pk = notif_id, user = request.user)
    except:
        messages.warning(request, 'Selected notification is already deleted (or) You do not have permission to delete it.')
    if notif_rec and notif_rec.user.id == request.user.id:
        notif_rec.delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def clear_creation_notification(request, notif_type):
    notif_rec = None
    try:
        if notif_type == "contributor":
            notif_rec = ContributorNotification.objects.filter(user = request.user).delete()
        elif notif_type == "admin":
            notif_rec = AdminReviewerNotification.objects.filter(user = request.user).delete()
        elif notif_type == "domain":
            notif_rec = DomainReviewerNotification.objects.filter(user = request.user).delete()
        elif notif_type == "quality":
            notif_rec = QualityReviewerNotification.objects.filter(user = request.user).delete()
    except:
        messages.warning(request, 'Something went wrong, contact site administrator.')

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
def creation_view_tutorial(request, foss, tutorial, lang):
    if not is_contributor(request.user) and not is_administrator(request.user):
        raise PermissionDenied()
    try:
        foss = unquote_plus(foss)
        tutorial = unquote_plus(tutorial)
        td_rec = TutorialDetail.objects.get(foss = FossCategory.objects.get(foss = foss), tutorial = tutorial)
        tr_rec = TutorialResource.objects.get(tutorial_detail = td_rec, language = Language.objects.get(name = lang))
        tr_recs = TutorialResource.objects.filter(tutorial_detail__in = TutorialDetail.objects.filter(foss = tr_rec.tutorial_detail.foss).order_by('order').values_list('id'), language = tr_rec.language)
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponseRedirect('/')
    video_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
    video_info = get_video_info(video_path)
    context = {
        'tr_rec': tr_rec,
        'tr_recs': sorted(tr_recs, key=lambda tutorial_resource: tutorial_resource.tutorial_detail.order),
        'ni_recs': NeedImprovementLog.objects.filter(tutorial_resource = tr_rec),
        'video_info': video_info,
        'media_url': settings.MEDIA_URL,
        'media_path': settings.MEDIA_ROOT,
        'tutorial_path': str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/',
        'script_base': settings.SCRIPT_URL,
    }
    return render(request, 'creation/templates/creation_view_tutorial.html', context)

@login_required
def creation_change_published_to_pending(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    if request.method == 'POST':
        form = PublishToPending(request.POST)
        if form.is_valid():
            try:
                row = TutorialResource.objects.get(tutorial_detail_id = request.POST.get('tutorial_name'), language_id = request.POST.get('language'))
                comp_title = row.tutorial_detail.foss.foss + ': ' + row.tutorial_detail.tutorial + ' - ' + row.language.name
                row.status = 0;
                row.save()
                add_contributor_notification(row, comp_title, 'This tutorial is unpublished for corrections.')
                messages.success(request, 'Tutorial unpublished successfully!')
                form = PublishToPending()
            except Exception, e:
                messages.error(request, str(e))
    else:
        form = PublishToPending()
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/creation_change_published_to_pending.html', context)

@csrf_exempt
def ajax_publish_to_pending(request):
    data = ''
    if request.method == 'POST':
        foss = ''
        lang = ''
        try:
            foss = request.POST.get('foss')
            lang = request.POST.get('lang')
        except:
            foss = ''
            lang = ''
        if foss and lang:
            td_list = TutorialDetail.objects.filter(foss_id = foss).values_list('id')
            tutorials = TutorialResource.objects.filter(tutorial_detail_id__in = td_list, language_id = lang, status = 1).distinct().order_by('tutorial_detail__level_id','tutorial_detail__order')
            for tutorial in tutorials:
                data += '<option value="' + str(tutorial.tutorial_detail.id) + '">' + tutorial.tutorial_detail.tutorial + '</option>'
            if data:
                data = '<option value="">Select Tutorial</option>' + data
        elif foss:
            languages = Language.objects.filter(id__in = TutorialResource.objects.filter(tutorial_detail__in = TutorialDetail.objects.filter(foss_id = foss).values_list('id'), status = 1).values_list('language_id').distinct())
            for language in languages:
                data += '<option value="' + str(language.id) + '">' + language.name + '</option>'
            if data:
                data = '<option value="">Select Language</option>' + data

    return HttpResponse(json.dumps(data), content_type='application/json')

@login_required
def creation_change_component_status(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    if request.method == 'POST':
        form = ChangeComponentStatusForm(request.POST)
        if form.is_valid():
            try:
                row = TutorialResource.objects.get(tutorial_detail_id = request.POST.get('tutorial_name'), language_id = request.POST.get('language'))
                comp_title = row.tutorial_detail.foss.foss + ': ' + row.tutorial_detail.tutorial + ' - ' + row.language.name
                status_list = {
                    0: 'Pending',
                    5: 'Need Improvement',
                    6: 'Not Required'
                }
                component = request.POST.get('component', '')
                status = status_list[int(request.POST.get('status', 0))]
                if component in ['outline', 'script', 'video']:
                    setattr(row, component + '_status', int(request.POST.get('status', 0)))
                    row.save()
                else:
                    setattr(row.common_content, component + '_status', int(request.POST.get('status', 0)))
                    row.common_content.save()
                add_contributor_notification(row, comp_title, component.title() + ' status has been changed to ' + status)
                messages.success(request, component.title() + ' status has been changed to ' + status)
                form = ChangeComponentStatusForm()
            except Exception, e:
                messages.error(request, str(e))
    else:
        form = ChangeComponentStatusForm()
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/creation_change_component_status.html', context)

@csrf_exempt
def ajax_change_component_status(request):
    data = ''
    if request.method == 'POST':
        foss = request.POST.get('foss', '')
        lang = request.POST.get('lang', '')
        tut = request.POST.get('tut', '')
        comp = request.POST.get('comp', '')
        if foss and lang and tut and comp:
            tr_rec = TutorialResource.objects.get(tutorial_detail_id = tut, language = lang)
            compValue = None
            data = '<option value="">Select Status</option><option value="0">Pending</option>'
            if comp in ['outline', 'script', 'video']:
                compValue = getattr(tr_rec, comp + '_status')
            else:
                compValue = getattr(tr_rec.common_content, comp + '_status')
            if compValue:
                data += '<option value="5">Need Improvement</option>'
            if comp in ['code', 'assignment','additional_material']:
                    data += '<option value="6">Not Required</option>'
        elif foss and lang:
            data = ['', '']
            td_list = TutorialDetail.objects.filter(foss_id = foss).values_list('id')
            lang_rec = Language.objects.get(pk = lang)
            tutorials = TutorialResource.objects.filter(tutorial_detail_id__in = td_list, language_id = lang, status = 0).distinct()
            data[0] = '<option value="">Select Tutorial Name</option>'
            data[1] = '<option value="outline">Outline</option><option value="script">Script</option>'
            for tutorial in tutorials:
                data[0] += '<option value="' + str(tutorial.tutorial_detail.id) + '">' + tutorial.tutorial_detail.tutorial + '</option>'
            if lang_rec.name == 'English':
                data[1] += '<option value="slide">Slides</option><option value="video">Video</option><option value="code">Codefiles</option><option value="assignment">Assignment</option><option value="prerequisite">Prerequisite</option><option value="keyword">Keywords</option><option value="additional_material">Additional material</option>'
            else:
                data[1] += '<option value="video">Video</option>'
            data[1] = '<option value="">Select Component</option>' + data[1]
        elif foss:
            languages = Language.objects.filter(id__in = TutorialResource.objects.filter(tutorial_detail__in = TutorialDetail.objects.filter(foss_id = foss).values_list('id'), status = 0).values_list('language_id').distinct())
            for language in languages:
                data += '<option value="' + str(language.id) + '">' + language.name + '</option>'
            if data:
                data = '<option value="">Select Language</option>' + data

    return HttpResponse(json.dumps(data), content_type='application/json')

def report_missing_component(request, trid):
    comps = {
        1: 'outline',
        2: 'script',
        3: 'video',
        4: 'slide',
        5: 'code',
        6: 'assignment'
    }
    try:
        tr_rec = TutorialResource.objects.get(pk = trid)
        comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
    except:
        raise PermissionDenied()
    form = TutorialMissingComponentForm(request.user)
    if request.method == 'POST':
        form = TutorialMissingComponentForm(request.user, request.POST)
        if form.is_valid():
            remarks = ''
            component = int(request.POST.get('component'))
            report_type = int(request.POST.get('report_type'))
            if report_type:
                remarks = request.POST.get('remarks')
            else:
                compStatus = 0
                compValue = ''
                if component <= 3:
                    compStatus = getattr(tr_rec, comps[component] + '_status')
                    compValue = getattr(tr_rec, comps[component])
                else:
                    compStatus = getattr(tr_rec.common_content, comps[component] + '_status')
                    compValue = getattr(tr_rec.common_content, comps[component])
                flag = 0
                if compStatus == 6:
                    flag = 1
                    messages.warning(request, 'The contributor of this tutorial says that the selected component is not required. However if you wish to report an error, please click on "Some content is missing" radio button.')
                elif compValue:
                    if component == 1:
                        flag = 1
                        messages.warning(request, 'The selected component is available. However if you wish to report an error, please click on "Some content is missing" radio button.')
                    if component <= 3:
                        if component != 1 and os.path.isfile(settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/' + compValue):
                            flag = 1
                            messages.warning(request, 'The selected component is available. However if you wish to report an error, please click on "Some content is missing" radio button.')
                    else:
                        if os.path.isfile(settings.MEDIA_ROOT + 'videos/resources/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/' + compValue):
                            flag = 1
                            messages.warning(request, 'The selected component is available. However if you wish to report an error, please click on "Some content is missing" radio button.')
                if flag:
                    context = {
                        'form': form,
                    }
                    context.update(csrf(request))
                    return render(request, 'creation/templates/report_missing_component.html', context)
            email = ''
            inform_me = request.POST.get('inform_me')
            if inform_me and request.user.is_authenticated() == False:
                email = request.POST.get('email', '')
            if request.user.is_authenticated():
                TutorialMissingComponent.objects.create(
                    user = request.user,
                    tutorial_resource = tr_rec,
                    component = component,
                    report_type = report_type,
                    remarks = remarks,
                    inform_me = inform_me,
                    email = email,
                )
            else:
                TutorialMissingComponent.objects.create(
                    tutorial_resource = tr_rec,
                    component = component,
                    report_type = report_type,
                    remarks = remarks,
                    inform_me = inform_me,
                    email = email,
                )
            add_contributor_notification(tr_rec, comp_title, 'Component missing form submitted by public')
            form = TutorialMissingComponentForm(request.user)
            messages.success(request, 'Thanks for submitting your query. Your query will be addressed shortly.')
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/report_missing_component.html', context)

def get_and_query_for_contributor_roles(data_rows, fields):
    query = None
    for row in data_rows:
        and_query = None # Query to search for a given term in each field
        counter = 0
        for field in fields:
            q = Q(**{"%s" % field: row[counter]})
            if and_query is None:
                and_query = q
            else:
                and_query = and_query & q
            counter = counter + 1
        if query is None:
            query = and_query
        else:
            query = query | and_query
    return query

def report_missing_component_reply(request, tmcid):
    if not is_contributor(request.user) and not is_administrator(request.user):
        raise PermissionDenied()
    tmc_row = None
    try:
        tmc_row = TutorialMissingComponent.objects.get(pk = tmcid)
    except:
        raise PermissionDenied()
    form = TutorialMissingComponentReplyForm()
    if request.method == 'POST':
        form = TutorialMissingComponentReplyForm(request.POST)
        if form.is_valid():
            TutorialMissingComponentReply.objects.create(missing_component = tmc_row, user = request.user, reply_message = request.POST.get('reply_message', ''))
            if tmc_row.inform_me:
                #send email
                to = []
                bcc = []
                cc = []
                username = "User"
                comps = {
                    1: 'Outline',
                    2: 'Script',
                    3: 'Video',
                    4: 'Slides',
                    5: 'Codefiles',
                    6: 'Assignment'
                }
                try:
                    if tmc_row.user:
                        to = [tmc_row.user.email]
                        username = tmc_row.user.first_name
                    else:
                        to = [tmc_row.email]
                    bcc = settings.ADMINISTRATOR_EMAIL
                except:
                    raise PermissionDenied()
                subject  = "Reply: Missing Component Reply Notifications"
                message = '''Dear {0},
You had posted Missing Component for the following tutorial:
Foss: {2}
Tutorial: {3}
Language: {4}
Component: {5}
Nature of Report: Component itself is missing
Following is the reply for your post:
{1}

--
Regards,
Spoken Tutorial
'''.format(username, request.POST.get('reply_message', ''), tmc_row.tutorial_resource.tutorial_detail.foss, tmc_row.tutorial_resource.tutorial_detail.tutorial, tmc_row.tutorial_resource.language, comps[tmc_row.component])
                # send email
                email = EmailMultiAlternatives(
                    subject, message, 'no-reply@spoken-tutorial.org',
                    to = to , bcc = bcc, cc = cc,
                    headers={'Reply-To': 'no-reply@spoken-tutorial.org', "Content-type":"text/html;charset=iso-8859-1"}
                )
                try:
                    result = email.send(fail_silently=False)
                except Exception, e:
                    print "*******************************************************"
                    print message
                    print "*******************************************************"
            messages.success(request, 'Reply message added successfully!')
            form = TutorialMissingComponentReplyForm()
    context = {
        'form': form,
        'tmc_row': tmc_row
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/report_missing_component_reply.html', context)

@login_required
def report_missing_component_list(request):
    if not is_contributor(request.user) and not is_administrator(request.user):
        raise PermissionDenied()
    rows = None
    if is_administrator(request.user):
        rows = TutorialMissingComponent.objects.all().order_by('-created')
    elif is_contributor(request.user):
        contrib_roles = list(ContributorRole.objects.filter(user = request.user).values_list('foss_category_id', 'language_id'))
        fields = ['tutorial_resource__tutorial_detail__foss_id', 'tutorial_resource__language_id']
        query = get_and_query_for_contributor_roles(contrib_roles, fields)
        rows = TutorialMissingComponent.objects.filter(query).order_by('-created')
    context = {
        'rows': rows
    }
    return render(request, 'creation/templates/report_missing_component_list.html', context)

@login_required
def suggest_topic(request):
    form = None
    if request.method == 'POST':
        form = SuggestTopicForm(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user_id = request.user.id
            form_data.save()
            for o in form.cleaned_data.get('operating_system'):
                form_data.operating_system.add(o)
            form = SuggestTopicForm()
            messages.success(request, 'Your suggestion for the Topic has been submitted to concerned person. We\'ll contact you soon.')
    else:
        form = SuggestTopicForm()
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/suggest_topic.html', context)

@login_required
def suggest_example(request):
    form = None
    if request.method == 'POST':
        form = SuggestExampleForm(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user_id = request.user.id
            form_data.save()
            form = SuggestExampleForm()
            messages.success(request, 'Your suggestion for the Example has been submitted to concerned person. We\'ll contact you soon.')
    else:
        form = SuggestExampleForm()
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/suggest_example.html', context)

@login_required
def collaborate(request):
    form = None
    if request.method == 'POST':
        form = CollaborateForm(request.POST)
        if form.is_valid():
            form_data = form.save(commit=False)
            form_data.user_id = request.user.id
            form_data.save()
            for o in form.cleaned_data.get('contribute_towards'):
                form_data.contribute_towards.add(o)
            form = CollaborateForm()
            messages.success(request, 'Form has been submitted to concerned person. Thank you for showing interest on collaborate with us. We\'ll contact you soon.')
    else:
        form = CollaborateForm()
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/collaborate.html', context)


@login_required
def update_prerequisite(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    form = UpdatePrerequisiteForm()
    if request.method == 'POST':
        form = UpdatePrerequisiteForm(request.POST)
        if form.is_valid():
            try:
                source_tutorial = TutorialDetail.objects.get(pk = form.cleaned_data['source_tutorial'] , foss_id = form.cleaned_data['source_foss'])
                tcc = TutorialCommonContent.objects.get(tutorial_detail = source_tutorial)
                if int(form.cleaned_data['destination_tutorial']) == 0:
                    tcc.prerequisite_id = None
                    tcc.prerequisite_status = 6
                    messages.success(request, 'Prerequisite for <b>' + source_tutorial.tutorial + '</b> updated to <b>Not Required</b>')
                else:
                    destination_tutorial = TutorialDetail.objects.get(pk = form.cleaned_data['destination_tutorial'] , foss_id = form.cleaned_data['destination_foss'])
                    tcc.prerequisite_id = destination_tutorial.id
                    tcc.prerequisite_status = 4
                    messages.success(request, 'Prerequisite <b>' + destination_tutorial.tutorial + '</b> updated to <b>' + source_tutorial.tutorial + '</b>.')
                tcc.save()
                return HttpResponseRedirect('/creation/update-prerequisite/')
            except Exception:
                pass
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/update_prerequisite.html', context)


@login_required
def update_keywords(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    form = UpdateKeywordsForm()
    if request.method == 'POST':
        form = UpdateKeywordsForm(request.POST)
        if form.is_valid():
            try:
                tcc = TutorialCommonContent.objects.get(tutorial_detail_id = request.POST.get('tutorial'))
                tcc.keyword = request.POST.get('keywords')
                tcc.keyword_user = request.user
                tcc.keyword_status = 4
                tcc.save()
                messages.success(request, 'Keywords updated successfully!')
                return HttpResponseRedirect('/creation/update-keywords/')
            except Exception, e:
                pass
    context = {
        'form': form
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/update_keywords.html', context)


@login_required
def update_sheet(request, sheet_type):
    sheet_types = ['instruction', 'installation', 'brochure']
    if not is_administrator(request.user) and not is_contributor(request.user) and not is_contenteditor(request.user)\
     or not sheet_type in sheet_types:
        raise PermissionDenied()
    form = UpdateSheetsForm()
    if request.method == 'POST':
        form = UpdateSheetsForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                foss_id = request.POST.get('foss')
                foss = FossCategory.objects.get(pk=foss_id)
                language_id = request.POST.get('language')
                language = Language.objects.get(pk=language_id)
                if sheet_type == 'brochure':
                  sheet_path = 'videos/' + str(foss.id) + '/' + \
                    foss.foss.replace(' ', '-') + '-' + sheet_type.title() + \
                    '-' + language.name + '.pdf'
                else:
                  sheet_path = 'videos/' + str(foss.id) + '/' + \
                    foss.foss.replace(' ', '-') + '-' + sheet_type.title() + \
                    '-Sheet-' + language.name + '.pdf'
                fout = open(settings.MEDIA_ROOT + sheet_path, 'wb+')
                f = request.FILES['comp']
                # Iterate through the chunks.
                for chunk in f.chunks():
                    fout.write(chunk)
                fout.close()
                messages.success(request, sheet_type.title() + \
                    'sheet uploaded successfully!')
                form = UpdateSheetsForm()
            except Exception, e:
                print e
    context = {
        'form': form,
        'sheet_type': sheet_type
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/update_sheet.html', context)


@csrf_exempt
def ajax_manual_language(request):
    data = ''
    if request.method == 'POST':
        foss_id = request.POST.get('foss', '')
        language_id = request.POST.get('language', '')
        sheet_type = request.POST.get('sheet_type', '')
        if foss_id and language_id and sheet_type:
            try:
                foss = FossCategory.objects.get(pk=foss_id)
                language = Language.objects.get(pk=language_id)
                sheet_path = 'videos/' + str(foss.id) + '/' + \
                    foss.foss + '-' + sheet_type.title() + '-Sheet-' + \
                    language.name + '.pdf'
                if os.path.isfile(settings.MEDIA_ROOT + sheet_path):
                    data = '<a href="' + settings.MEDIA_URL + sheet_path + \
                    '" target="_blank"> Click here to view the currently \
                    available instruction sheet for the tutorial selected \
                    above</a>'
            except Exception, e:
                print e
                pass
        elif foss_id:
            tutorials = TutorialResource.objects.filter(
                Q(status=1) | Q(status=2),
                tutorial_detail__foss_id=foss_id
            ).values_list(
                'language_id',
                'language__name'
            ).order_by('language__name').distinct()
            for tutorial in tutorials:
                data += '<option value="' + str(tutorial[0]) + '">' + \
                    str(tutorial[1]) + '</option>'
            if data:
                data = '<option value="">-- Select Language --</option>' + data
    return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def ajax_get_tutorials(request):
    data = ''
    if request.method == 'POST':
        foss_id = request.POST.get('foss', '')
        if foss_id:
            tutorials = TutorialResource.objects.filter(
                Q(status=1) | Q(status=2),
                tutorial_detail__foss_id=foss_id
            ).values_list(
                'tutorial_detail_id',
                'tutorial_detail__tutorial'
            ).order_by('tutorial_detail__tutorial').distinct()
            for tutorial in tutorials:
                data += '<option value="' + str(tutorial[0]) + '">' + \
                    str(tutorial[1]) + '</option>'
            if data:
                data = '<option value="">-- Select Tutorial --</option>' + data
    return HttpResponse(json.dumps(data), content_type='application/json')

def view_brochure(request):
    template = 'creation/templates/view_brochure.html'
    my_dict = services.get_data_for_brochure_display()
    context = {
        'my_dict': my_dict
    }
    return render(request, template, context)

@login_required
def update_assignment(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    form = UpdateAssignmentForm()
    if request.method == 'POST':
        form = UpdateAssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                foss_id = request.POST.get('foss')
                foss = FossCategory.objects.get(pk=foss_id)

                tutorial_detail_id = request.POST.get('tutorial')
                tutorial = TutorialDetail.objects.get(pk=tutorial_detail_id)
                file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                file_name =  tutorial.tutorial.replace(' ', '-') + '-Assignment' + file_extension
                file_path = settings.MEDIA_ROOT + 'videos/' + str(foss_id) + '/' + str(tutorial_detail_id) + '/resources/' + file_name
            
                fout = open(file_path, 'wb+')
                f = request.FILES['comp']
                # Iterate through the chunks.
                for chunk in f.chunks():
                    fout.write(chunk)
                fout.close()

                tr_res = TutorialResource.objects.get(tutorial_detail=tutorial_detail_id, language_id = 22)
                tr_res.common_content.assignment = file_name
                tr_res.common_content.assignment_status = 4
                tr_res.common_content.assignment_user = request.user
                tr_res.common_content.save()



                messages.success(request, 'Assignment updated successfully!')
                form = UpdateAssignmentForm()
            except Exception, e:
                print e
    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/update_assignment.html', context)

