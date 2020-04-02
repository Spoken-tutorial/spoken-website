import json
import os
import re
import subprocess
import time
import collections
from django.utils import timezone
from decimal import Decimal
try:
    from urllib.parse import quote, unquote_plus
    from urllib.request import urlopen
except ImportError:
    from urllib.parse import quote, unquote_plus
    from urllib.request import urlopen

# Third Party Stuff
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.shortcuts import render,redirect

# Spoken Tutorial Stuff
from cms.sortable import *
from creation.forms import *
from creation.models import *
from creation.subtitles import *

from . import services
from django.utils import timezone
from datetime import datetime,timedelta
from creation.filters import CreationStatisticsFilter, ContributorRatingFilter, ReviewerFilter
from django.db.models import Count, Min, Q, Sum, F
import itertools
from django.utils.html import format_html
from django.core.urlresolvers import reverse

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
    if user.groups.filter(Q(name = 'Contributor')|Q(name = 'External-Contributor')).count():
        return True
    return False

def is_internal_contributor(user):
    """Check if the user is having contributor rights"""
    if user.groups.filter(name = 'Contributor').count():
        return True
    return False

def is_external_contributor(user):
    """Check if the user is having external-contributor rights"""
    if user.groups.filter(name = 'External-Contributor').count():
        return True
    return False

def is_videoreviewer(user):
    """Check if the user is having video reviewer rights"""
    if user.groups.filter(name = 'Video-Reviewer').count() == 1:
        return True
    return False

def is_domainreviewer(user):
    """Check if the user is having domain reviewer rights"""
    if user.groups.filter(name = 'Domain-Reviewer').count() == 1:
        return True
    return False

def is_qualityreviewer(user):
    """Check if the user is having quality reviewer rights"""
    if user.groups.filter(name = 'Quality-Reviewer').count() == 1:
        return True
    return False

def is_administrator(user):
    """Check if the user is having administrator rights"""
    if user.groups.filter(name = 'Administrator').count():
        return True
    return False

def is_contenteditor(user):
    """Check if the user is having Content-Editor rights"""
    if user.groups.filter(name = 'Content-Editor').count():
        return True
    return False

def is_language_manager(user):
    """ Check if the logged in user is Language Manager"""
    return LanguageManager.objects.filter(user=user,status=1).exists()

def get_filesize(path):
    filesize_bytes = os.path.getsize(path)
    return humansize(filesize_bytes)

# returns video meta info using ffmpeg
def get_video_info(path):
    """Uses ffmpeg to determine information about a video."""
    info_m = {}
    try:
        process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', path], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        stdout, stderr = process.communicate()
        duration_m = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?)", stdout.decode('utf-8'), re.DOTALL).groupdict()
        info_m = re.search(r": Video: (?P<codec>.*?), (?P<profile>.*?), (?P<width>.*?)x(?P<height>.*?), ", stdout.decode('utf-8'), re.DOTALL).groupdict()

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
#create_thumbnail(tr_rec, 'Big', tr_rec.video_thumbnail_time, '700:500')
def create_thumbnail(row, attach_str, thumb_time, thumb_size):
    filepath = settings.MEDIA_ROOT + 'videos/' + str(row.tutorial_detail.foss_id) + '/' + str(row.tutorial_detail_id) + '/'
    filename = row.tutorial_detail.tutorial.replace(' ', '-') + '-' + attach_str + '.png'
    try:
        #process = subprocess.Popen(['/usr/bin/ffmpeg', '-i ' + filepath + row.video + ' -r ' + str(30) + ' -ss ' + str(thumb_time) + ' -s ' + thumb_size + ' -vframes ' + str(1) + ' -f ' + 'image2 ' + filepath + filename], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', filepath + row.video, '-r', str(30), '-ss', str(thumb_time), '-s', thumb_size, '-vframes', str(1), '-f', 'image2', filepath + filename], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        stdout, stderr = process.communicate()
        if stderr:
            print((filepath + filename))
            print(stderr)
    except Exception as e:
        print((1, e))
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
    con_roles = ContributorRole.objects.filter(tutorial_detail = tr_rec.tutorial_detail, language = tr_rec.language, status = 1)

    for con in con_roles:
        ContributorNotification.objects.create(user = con.user, title = comp_title, message = message, tutorial_resource = tr_rec)

ROLES_DICT = {
        'contributor': 0,
        'external-contributor': 1,
        'video-reviewer': 2,
        'domain-reviewer': 3,
        'quality-reviewer': 4,
    }

ASSIGNMENT_STATUS_DICT = {
    'un-assigned': 0,
    'assigned': 1
}

SCRIPT_STATUS_DICT = {
    'not-started': 0,
    'written': 1,
    'domain-approved': 2,
    'quality-approved': 3,
    'uploaded': 4
}

STATUS_DICT = {
    'inactive': 0,
    'active': 1
}


@login_required
def creation_add_role(request, role_type,languages):

    # Add multiple languages to the user
    language_ids  = languages.split('/')
    for lang_id in language_ids:
        print("lang_id : ",lang_id)
        if role_type in ROLES_DICT:
            if role_type != 'video-reviewer':
                if lang_id:
                    language_alert = Language.objects.get(id = int(lang_id))

            this_user_role = RoleRequest.objects.filter(user = request.user,
                role_type = ROLES_DICT[role_type], language_id = int(lang_id))

            if this_user_role.exists():

                if this_user_role.filter(status = 0).exists():
                    if role_type == 'video-reviewer':
                        messages.warning(request, 'Request to the ' +
                            role_type.title() + ' role is already waiting for admin approval!')
                    else:
                        messages.warning(request, 'Request to the ' +
                            role_type.title() + ' role'+ ' for ' + language_alert.name +
                            ' is already waiting for admin approval!')
                if this_user_role.filter(status = 2).exists():
                    this_user_role.update(status = 0)
            else:
                new_role_request = RoleRequest()
                new_role_request.user = request.user
                new_role_request.role_type = ROLES_DICT[role_type]
                if role_type != 'video-reviewer':
                    new_role_request.language = language_alert
                new_role_request.status = STATUS_DICT['inactive']
                new_role_request.save()
                #RoleRequest.objects.create(user = request.user, role_type = ROLES_DICT[role_type],
                                           #language_id = int(lang_id), status = 0)
                #new_role_request.user.groups.add(Group.objects.get(
                #    name = role_type))
                if role_type != 'video-reviewer':
                    messages.success(request, 'Request to the ' + \
                            role_type.title() +' role'+' for the language ' +\
                            language_alert.name+' has been sent for admin approval!')
                else:
                    messages.success(request, 'Request to the ' + \
                            role_type.title() +' role has been sent for approval!')

        else:
            messages.error(request, 'Invalid role argument!')


    return HttpResponseRedirect('/creation/')

@login_required
def creation_accept_role_request(request, recid, user_type):
    if is_administrator:
        roles = {
            0: 'Contributor',
            1: 'External-Contributor',
            2: 'Video-Reviewer',
            3: 'Domain-Reviewer',
            4: 'Quality-Reviewer',
        }
        try:
            role_rec = RoleRequest.objects.get(pk = recid, status = STATUS_DICT['inactive'])
            if role_rec.role_type in roles:
                try:
                    role_rec.user.groups.add(Group.objects.get(name = roles[role_rec.role_type]))
                    role_rec.approved_user = request.user
                    role_rec.status = 1
                    role_rec.save()
                    if role_rec.role_type == ROLES_DICT['video-reviewer']:
                        messages.success(request, roles[role_rec.role_type] +' role is added to '+role_rec.user.username)
                        add_creation_notification(request, role_rec.role_type, role_rec.user_id , role_rec.language)
                    else:
                        messages.success(request, roles[role_rec.role_type] +' role is added to ' + role_rec.user.username + ' for the language '+role_rec.language.name)
                        add_creation_notification(request, role_rec.role_type, role_rec.user_id , role_rec.language)
                        if int(role_rec.role_type) in (ROLES_DICT['contributor'],ROLES_DICT['external-contributor']):
                            print("Okay 1 ",role_rec.role_type)
                            add_contributorrating(role_rec)
                except Exception as e:
                    print (e)
                    messages.error(request, role_rec.user.username + ' is already having ' + roles[role_rec.role_type] + ' role or Language field is not present')
            else:
                messages.error(request, 'Invalid role argument!')
        except:
            messages.error(request, 'The given role request id is either invalid or it is already accepted')
    else:
        raise PermissionDenied()
    if user_type == 'lang_manager':
        return HttpResponseRedirect('/creation/role/lang_requests/' + roles[role_rec.role_type].lower() + '/')
    else:
        return HttpResponseRedirect('/creation/role/requests/' + roles[role_rec.role_type].lower() + '/')

@login_required
def creation_reject_role_request(request, recid, user_type):
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
            role_rec.delete()
            messages.success(request, roles[role_rec.role_type]+
            ' role of '+ str(role_rec.language) +
            ' has been deleted successfully for '+role_rec.user.username)
        except:
            messages.error(request, 'The given role request id is either invalid or it is already rejected')
    else:
        raise PermissionDenied()
    if user_type == 'lang_manager':
        return HttpResponseRedirect('/creation/role/lang_requests/' + roles[role_rec.role_type].lower() + '/')
    else:
        return HttpResponseRedirect('/creation/role/requests/' + roles[role_rec.role_type].lower() + '/')

@login_required
def creation_revoke_role_request(request, role_type,languages):

    group_role_id = {
            0: 'Contributor',
            1: 'External-Contributor',
            2: 'Video-Reviewer',
            3: 'Domain-Reviewer',
            4: 'Quality-Reviewer',
        }

    # Revoke multiple languages from the user
    lang_ids = languages.split('/')
    for a_language in lang_ids:
        a_language = int(a_language)
        if role_type in ROLES_DICT:
            try:
                role_rec = RoleRequest.objects.get(
                    user = request.user, role_type = ROLES_DICT[role_type],
                    status = 1,language_id = a_language)
                if role_rec.role_type != ROLES_DICT['video-reviewer']:
                    if role_rec.role_type == ROLES_DICT['contributor'] or role_rec.role_type == ROLES_DICT['external-contributor']:
                        try:
                            contrib_roles=ContributorRole.objects.filter(user = role_rec.user, language_id = a_language)
                            for role in contrib_roles:
                                role.revoke()
                        except ContributorRole.DoesNotExist:
                            # The user has not Contributed anything
                            pass
                    elif role_rec.role_type == 3:
                        try:
                            DomainReviewerRole.objects.get(user_id = role_rec.user.id, language_id = a_language).revoke()
                        except DomainReviewerRole.DoesNotExist:
                            # The user has not worked on any Domain
                            pass
                    elif role_rec.role_type == 4:
                        try:
                            QualityReviewerRole.objects.get(user = role_rec.user, language_id = a_language).revoke()
                        except QualityReviewerRole.DoesNotExist:
                            # The user has not worked on any Quality
                            pass

                    role_rec.revoke()
                    lang_show = Language.objects.get(id = a_language)
                    messages.success(request, role_type.title() + ' role has been revoked from ' + role_rec.user.username+' for the language '+ lang_show.name)

            except RoleRequest.DoesNotExist:
                # This will be hit only when the request type is video-reviewer
                role_rec = RoleRequest.objects.get(
                    user = request.user, role_type = ROLES_DICT[role_type],
                    status = 1)
                role_rec.revoke()
                messages.warning(request, 'Role is revoked!')
        else:
            messages.error(request, 'Invalid role type argument!')

    role_count = RoleRequest.objects.filter(user = request.user,role_type = ROLES_DICT[role_type],status = 1)
    if not role_count.exists():
        request.user.groups.remove(Group.objects.get(name = group_role_id[ROLES_DICT[role_type]]))

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
def creation_lang_list_role_requests(request, tabid = 'contributor'):
    if is_language_manager:
        language_manager_langs = LanguageManager.objects.filter(
            user_id= request.user.id).values_list('language_id')
        contrib_recs = RoleRequest.objects.filter(role_type = 0,
            status = 0, language_id__in= language_manager_langs).order_by('-updated')
        ext_contrib_recs = RoleRequest.objects.filter(role_type = 1,
            status = 0, language_id__in= language_manager_langs).order_by('-updated')
        context = {
            'tabid': tabid,
            'contrib_recs': contrib_recs,
            'ext_contrib_recs': ext_contrib_recs,
        }
        return render(request, 'creation/templates/creation_lang_list_role_requests.html', context)
    else:
        raise PermissionDenied()

# This is handled by management file, kept  here for backup.
# This can be run manually by hitting /creation/refresh_roles url
@login_required
def refresh_roles(request):
    if is_administrator(request.user):
        contrib_count = 0
        domain_count = 0
        quality_count = 0
        contributor_roles = ContributorRole.objects.filter(status = 1).values('user_id','language_id').distinct()
        domain_roles = DomainReviewerRole.objects.filter(status = 1).values('user_id','language_id').distinct()
        quality_roles = QualityReviewerRole.objects.filter(status = 1).values('user_id','language_id').distinct()
        for contributor in contributor_roles:
            role_request = RoleRequest.objects.filter(
                Q(role_type = ROLES_DICT['contributor'])|Q(role_type = ROLES_DICT['external-contributor']),
                user_id = contributor['user_id'],language_id = contributor['language_id'])
            if not role_request.exists():
                contrib_user = User.objects.get(id = contributor['user_id'])
                role_request = RoleRequest()
                role_request.user = contrib_user
                role_request.language = Language.objects.get(id = contributor['language_id'])
                if is_contributor(contrib_user):
                    role_request.role_type = ROLES_DICT['contributor']
                elif is_external_contributor(contrib_user):
                    role_request.role_type = ROLES_DICT['external-contributor']
                role_request.status = 1
                role_request.save()
                contributor_with_rating = \
                ContributorRating.objects.filter(user_id = contributor['user_id'],
                                           language_id = contributor['language_id'])
                if not contributor_with_rating.exists():
                    new_contrib_rating_request = ContributorRating()
                    new_contrib_rating_request.user_id = contributor['user_id']
                    new_contrib_rating_request.language_id = contributor['language_id']
                    new_contrib_rating_request.save()
                contrib_count += 1
            else:
                role_request.update(status =  STATUS_DICT['active'],
                    approved_user_id = request.user.id)
        messages.success(request,str(contrib_count)+ " Contributors added")

        for domain_reviewer in domain_roles:
            role_request = RoleRequest.objects.filter( role_type = ROLES_DICT['domain-reviewer'],
                user_id = domain_reviewer['user_id'],language_id = domain_reviewer['language_id'])
            if not role_request.exists():
                role_request = RoleRequest()
                role_request.user = User.objects.get(id = domain_reviewer['user_id'])
                role_request.language = Language.objects.get(id = domain_reviewer['language_id'])
                role_request.role_type = ROLES_DICT['domain-reviewer']
                role_request.status = STATUS_DICT['active']
                role_request.save()
                domain_count += 1
            else:
                role_request.update(status =  STATUS_DICT['active'],
                    approved_user_id = request.user.id)

        messages.success(request,str(domain_count)+ " Domain Reviewers added")

        for quality_reviewer in quality_roles:
            role_request = RoleRequest.objects.filter(role_type = ROLES_DICT['quality-reviewer'],
                user_id = quality_reviewer['user_id'],language_id = quality_reviewer['language_id'])
            if not role_request.exists():
                role_request = RoleRequest()
                role_request.user = User.objects.get(id = quality_reviewer['user_id'])
                role_request.language = Language.objects.get(id = quality_reviewer['language_id'])
                role_request.role_type = ROLES_DICT['quality-reviewer']
                role_request.status = STATUS_DICT['active']
                role_request.save()
                quality_count += 1
            else:
                role_request.update(status =  STATUS_DICT['active'],
                    approved_user_id = request.user.id)
        messages.success(request,str(quality_count)+ " Quality Reviewers added")
        return HttpResponseRedirect('/creation')
    else:
        messages.error(request,"Not enough permissions to perform this operation")
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
    except Exception as e:
        messages.error(request, str(e))
    return HttpResponseRedirect('/creation/')

# Creation app dashboard
@login_required
def creationhome(request):
    # Get languages for he is an approved Contributor /..
    is_contributor_langs             =   services.get_revokable_languages_for_role(request.user,'contributor')
    is_external_contributor_langs    =   services.get_revokable_languages_for_role(request.user,'external-contributor')
    is_domain_reviewer_langs         =   services.get_revokable_languages_for_role(request.user,'domain-reviewer')
    is_quality_reviewer_langs        =   services.get_revokable_languages_for_role(request.user,'quality-reviewer')
    not_contributor_langs = Language.objects.exclude(id__in = is_contributor_langs.values('id')).values('id','name')
    not_external_contributor_langs = Language.objects.exclude(id__in = is_external_contributor_langs.values('id')).values('id','name')
    not_domain_reviewer_langs = Language.objects.exclude(id__in = is_domain_reviewer_langs.values('id')).values('id','name')
    not_quality_reviewer_langs = Language.objects.exclude(id__in = is_quality_reviewer_langs.values('id')).values('id','name')

    languages = Language.objects.filter().values('name')
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
            'is_creation_role': True,
            'is_contributor_language': is_contributor_langs,
            'is_external_contributor_language': is_external_contributor_langs,
            'is_domain_reviewer_language': is_domain_reviewer_langs,
            'is_quality_reviewer_language': is_quality_reviewer_langs,
            'contributor_language': not_contributor_langs,
            'external_contributor_language': not_external_contributor_langs,
            'domain_reviewer_language': not_domain_reviewer_langs,
            'quality_reviewer_language': not_quality_reviewer_langs,
            'language': languages
        }
        context.update(csrf(request))
        return render(request, 'creation/templates/creationhome.html', context)
    else:

        context = {
            'is_creation_role': False,
            'contributor_language': not_contributor_langs,
            'external_contributor_language': not_external_contributor_langs,
            'domain_reviewer_language': not_domain_reviewer_langs,
            'quality_reviewer_language': not_quality_reviewer_langs,
            'language': languages
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
                tutorial_resource.save()

            return HttpResponseRedirect('/creation/upload/tutorial/' + str(tutorial_resource.id) + '/')
    else:
        form = UploadTutorialForm(user = request.user)

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
        form = UploadPublishTutorialForm(user = request.user)

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
                data += '<option value = "' + str(td_rec.id) + '">' + td_rec.tutorial + '</option>'
            if data:
                data = '<option value = "">Select Tutorial</option>' + data
    return HttpResponse(json.dumps(data), content_type = 'application/json')

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
                data += '<option value = "' + str(tutorial.id) + '">' + tutorial.tutorial + '</option>'
            if data:
                data = '<option value = "">Select Tutorial</option>' + data
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
                td_list = ContributorRole.objects.filter(
                    tutorial_detail__foss_id = foss,
                    user_id = request.user.id,
                    language_id = lang_rec,
                    status = 1).values_list('tutorial_detail_id')
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
                data += '<option value = "' + str(tutorial.id) + '">' + tutorial.tutorial + '</option>'
            if data:
                data = '<option value = "">Select Tutorial</option>' + data
        elif foss:
            languages = Language.objects.filter(id__in = ContributorRole.objects.filter(user_id = request.user.id, tutorial_detail__foss_id = foss).values_list('language_id'))
            for language in languages:
                data += '<option value = "' + str(language.id) + '">' + language.name + '</option>'
            if data:
                data = '<option value = "">Select Language</option>' + data

    return HttpResponse(json.dumps(data), content_type = 'application/json')

@csrf_exempt
def ajax_get_keywords(request):
    data = ''
    if request.method == 'POST':
        try:
            tutorial_detail_id = int(request.POST.get('tutorial_detail'))
            tcc = TutorialCommonContent.objects.get(tutorial_detail_id = tutorial_detail_id)
            data = tcc.keyword
        except Exception as e:
            pass
    return HttpResponse(json.dumps(data), content_type = 'application/json')

@login_required
def upload_tutorial(request, trid):
    tr_rec = None
    contrib_log = None
    review_log = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        ContributorRole.objects.get(user_id = request.user.id, tutorial_detail_id = tr_rec.tutorial_detail_id, language_id = tr_rec.language_id, status = 1)
        contrib_log = ContributorLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_log = NeedImprovementLog.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
    except Exception as e:
        print(e)
        raise PermissionDenied()
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
        ContributorRole.objects.get(user_id = request.user.id, tutorial_detail_id = tr_rec.tutorial_detail, language_id = tr_rec.language_id, status = 1)
    except Exception as e:
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
            except Exception as e:
                print(e)
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
        ContributorRole.objects.get(user_id = request.user.id, tutorial_detail_id = tr_rec.tutorial_detail, language_id = tr_rec.language_id, status = 1)
    except Exception as e:
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
                except Exception as e:
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
            except Exception as e:
                print(e)
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
            except Exception as e:
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
        ContributorRole.objects.get(user_id = request.user.id,
        	tutorial_detail_id = tr_rec.tutorial_detail.id,
        	language_id = tr_rec.language_id, status = 1)
    except Exception as e:
        print(e)
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
                except Exception as e:
                    code = e.code
                if(int(code) == 200):
                    tr_rec.timed_script = storage_path
                    tr_rec.save()
                    srt_file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/' + tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-English.srt'
                    minified_script_url = settings.SCRIPT_URL.strip('/') + '?title = ' + quote(storage_path) + '&printable = yes'
                    if generate_subtitle(minified_script_url, srt_file_path):
                        messages.success(request, 'Timed script updated and subtitle file generated successfully!')
                    else:
                        messages.success(request, 'Timed script updated successfully! But there is a in generating subtitle file.')
                    return HttpResponseRedirect('/creation/upload/timed-script/')
                else:
                    messages.error(request, 'Please update the timed-script to wiki before pressing the submit button.')
            except Exception as e:
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
        data = '<option value = "">Select Tutorial Name</option>'
        for row in rows:
            data += '<option value = "' + str(row.id) + '">' + row.tutorial + '</option>'
    return HttpResponse(json.dumps(data), content_type = 'application/json')

@login_required
def upload_prerequisite(request, trid):
    tr_rec = None
    try:
        tr_rec = TutorialResource.objects.get(pk = trid, status = 0)
        ContributorRole.objects.get(user_id = request.user.id, tutorial_detail_id = tr_rec.tutorial_detail, language_id = tr_rec.language_id, status = 1)
    except Exception as e:
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
            except Exception as e:
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
        ContributorRole.objects.get(user_id = request.user.id, tutorial_detail_id = tr_rec.tutorial_detail, language_id = tr_rec.language_id, status = 1)
    except Exception as e:
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
            except Exception as e:
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
        ContributorRole.objects.get(user_id = request.user.id, tutorial_detail_id = tr_rec.tutorial_detail_id, language_id = tr_rec.language_id, status = 1)
        comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
    except Exception as e:
        raise PermissionDenied()
    if component == 'video' and getattr(tr_rec, component + '_status') == 4:
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
                    if component == 'video':
                        file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                        file_name = tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-' + tr_rec.language.name + file_extension
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
                        comp_log.status = tr_rec.video_status
                        tr_rec.video = file_name
                        tr_rec.video_user = request.user
                        tr_rec.video_status = 1
                        if not tr_rec.version:
                            tr_rec.version = 1
                        tr_rec.video_thumbnail_time = '00:' + request.POST.get('thumb_mins', '00') + ':' + request.POST.get('thumb_secs', '00')
                        tr_rec.save()
                        if tr_rec.language.name == 'English':
                            create_thumbnail(tr_rec, 'Big', tr_rec.video_thumbnail_time, '700:500')
                            create_thumbnail(tr_rec, 'Small', tr_rec.video_thumbnail_time, '170:127')
                        comp_log.save()
                        comp_title = tr_rec.tutorial_detail.foss.foss + ': ' + tr_rec.tutorial_detail.tutorial + ' - ' + tr_rec.language.name
                        add_adminreviewer_notification(tr_rec, comp_title, 'Video waiting for admin review')
                        response_msg = 'Video uploaded successfully!'
                    elif component == 'slide':
                        file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                        file_name = tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Slides' + file_extension
                        file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/resources/' + file_name
                        fout = open(file_path, 'wb+')
                        f = request.FILES['comp']
                        # Iterate through the chunks.
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
                        file_name = tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Codefiles' + file_extension
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
                        file_name = tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Assignment' + file_extension
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
                        file_name = tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Additionalmaterial' + file_extension
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
                except Exception as e:
                    print(e)
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
        ContributorRole.objects.get(user_id = request.user.id, tutorial_detail_id = tr_rec.tutorial_detail, language_id = tr_rec.language_id, status = 1)
    except Exception as e:
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
    except Exception as e:
        messages.error(request, 'Something went wrong, please try after some time.')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


def view_component(request, trid, component):
    tr_rec = None
    context = {}
    try:
        tr_rec = TutorialResource.objects.get(pk = trid)
    except Exception as e:
        print(e)
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
    elif component == 'video':
        video_path = settings.MEDIA_ROOT + "videos/" + str(tr_rec.tutorial_detail.foss_id) + "/" + str(tr_rec.tutorial_detail_id) + "/" + tr_rec.video
        video_info = get_video_info(video_path)
        context = {
            'tr': tr_rec,
            'component': component,
            'video_info': video_info,
            'media_url': settings.MEDIA_URL
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
                    print((counter, tmp_rec.tutorial_detail.tutorial))
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
            tmp_recs = TutorialResource.objects.filter(status = 0)
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
                    print((counter, tmp_rec.tutorial_detail.tutorial))
                counter += 1
            page = request.GET.get('page')
            tmp_recs = get_page(tmp_recs, page, 50)
        except Exception as e:
            print(e)
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
        collection = ReviewerFilter(request.POST, queryset=collection)
        form = collection.form
        context = {
            'collection': collection.qs,
            'header': header,
            'ordering': ordering,
            'script_url': settings.SCRIPT_URL,
            'form': form
        }
        return render(request, 'creation/templates/admin_review_index.html', context)
    except Exception as e:
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
                except Exception as e:
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
                except Exception as e:
                    error_msg = 'Something went wrong, please try again later.'
            else:
                error_msg = 'Invalid status code!'
    else:
        form = ReviewVideoForm()
    video_path = settings.MEDIA_ROOT + "videos/" + str(tr.tutorial_detail.foss_id) + "/" + str(tr.tutorial_detail_id) + "/" + tr.video
    video_info = get_video_info(video_path)
    if error_msg:
        messages.error(request, error_msg)
    if response_msg:
        messages.success(request, response_msg)
    context = {
        'tr': tr,
        'form': form,
        'media_url': settings.MEDIA_URL,
        'video_info': video_info,
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
        collection = ReviewerFilter(request.POST, queryset=collection)
        form = collection.form
        page = request.GET.get('page')
        collection = get_page(collection.qs, page)
    except:
        messages.error('Something went wrong, Please try again later.')
    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering,
        'form': form
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
            14: SortableHeader('<span title = "" data-original-title = "" class = "fa fa-cogs fa-2"></span>', False, '', 'col-center')
        }
        collection = TutorialResource.objects.filter(id__in=tmp_ids)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        collection = ReviewerFilter(request.POST, queryset=collection)
        form = collection.form
        page = request.GET.get('page')
        collection = get_page(collection.qs, page)
    except Exception as e:
        print(e)
    context = {
        'collection': collection,
        'form': form,
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
                except Exception as e:
                    print(e)
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
        collection = ReviewerFilter(request.POST, queryset=collection)
        form = collection.form
        page = request.GET.get('page')
        collection = get_page(collection.qs, page)
    except:
        messages.error('Something went wrong, Please try again later.')
    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering,
        'form': form
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
    qr_roles = QualityReviewerRole.objects.filter(user_id = request.user.id, status = 1)
    for rec in qr_roles:
        if rec.language.name == 'English':
            tr_recs = TutorialResource.objects.filter(Q(outline_status = 3) | Q(script_status = 3) | Q(video_status = 3) | Q(common_content__slide_status = 3) | Q(common_content__code_status = 3) | Q(common_content__assignment_status = 3) | Q(common_content__keyword_status = 3) | Q(common_content__prerequisite_status = 3) | Q(common_content__additional_material_status = 3), Q(tutorial_detail__foss_id = rec.foss_category_id) & Q(language_id = rec.language_id) & Q(status = 0))
        else:
            tr_recs = TutorialResource.objects.filter(Q(outline_status = 3) | Q(script_status = 3) | Q(video_status = 3), Q(tutorial_detail__foss_id = rec.foss_category_id) & Q(language_id = rec.language_id) & Q(status = 0)).order_by('updated')

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
            14: SortableHeader('<span title = "" data-original-title = "" class = "fa fa-cogs fa-2"></span>', False, '', 'col-center')
        }
        collection = TutorialResource.objects.filter(id__in = tmp_ids)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        collection = ReviewerFilter(request.POST, queryset=collection)
        form = collection.form
        page = request.GET.get('page')
        collection = get_page(collection.qs, page)
    except Exception as e:
        print(e)

    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering,
        'form': form
    }
    return render(request, 'creation/templates/quality_review_index.html', context)


def publish_tutorial_index(request):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tmp_ids = []
    qr_roles = QualityReviewerRole.objects.filter(user_id = request.user.id, status = 1)
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
            14: SortableHeader('<span title = "" data-original-title = "" class = "fa fa-cogs fa-2"></span>', False, '', 'col-center')
        }
        collection = TutorialResource.objects.filter(id__in = tmp_ids)
        collection = get_sorted_list(request, collection, header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        collection = ReviewerFilter(request.POST, queryset=collection)
        form = collection.form
        page = request.GET.get('page')
        collection = get_page(collection.qs, page)
    except:
        pass

    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering,
        'form': form
    }
    return render(request, 'creation/templates/publish_tutorial_index.html', context)


def public_review_tutorial_index(request):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tmp_ids = []
    qr_roles = QualityReviewerRole.objects.filter(user_id = request.user.id, status = 1)
    tr_recs = ''
    for rec in qr_roles:
        if rec.language.name != 'English':
            tr_recs = TutorialResource.objects.filter(Q(outline_status__gt = 0) & Q(outline_status__lt = 5), Q(script_status__gt = 0) & Q(script_status__lt = 5), Q(video_status__gt = 0) & Q(video_status__lt = 5), Q(tutorial_detail__foss_id = rec.foss_category_id) & Q(language_id = rec.language_id) & Q(status = 0)).order_by('updated')

        for tr_rec in tr_recs:
            tmp_ids.append(tr_rec.id)

    collection = None
    header = ''
    ordering = ''
    form = ''
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
                14: SortableHeader('<span title = "" data-original-title = "" class = "fa fa-cogs fa-2"></span>', False, '', 'col-center')
            }
            collection = TutorialResource.objects.filter(id__in = tmp_ids)
            collection = get_sorted_list(request, collection, header, raw_get_data)
            ordering = get_field_index(raw_get_data)
            collection = ReviewerFilter(request.POST, queryset=collection)
            form = collection.form
            page = request.GET.get('page')
            collection = get_page(collection.qs, page)
    except Exception as e:
        print(e)

    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering,
        'form': form
    }
    return render(request, 'creation/templates/public_review_tutorial_index.html', context)


@login_required
def public_review_list(request):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tmp_ids = []
    qr_roles = QualityReviewerRole.objects.filter(user_id = request.user.id, status = 1)
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
                14: SortableHeader('<span title = "" data-original-title = "" class = "fa fa-cogs fa-2"></span>', False, '', 'col-center', 'colspan = 2')
            }
            collection = TutorialResource.objects.filter(id__in = tmp_ids)
            collection = get_sorted_list(request, collection, header, raw_get_data)
            ordering = get_field_index(raw_get_data)
            collection = ReviewerFilter(request.POST, queryset=collection)
            form = collection.form
            page = request.GET.get('page')
            collection = get_page(collection.qs, page)
    except:
        pass

    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering,
        'form': form
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
    except Exception as e:
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
                except Exception as e:
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
        # add tutorials available here
        refresh_tutorials(request, tr_rec)
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
        collection = ReviewerFilter(request.POST, queryset=collection)
        form = collection.form
        collection = get_page(collection.qs, page)
    except:
        messages.error('Something went wrong, Please try again later.')
    context = {
        'collection': collection,
        'header': header,
        'ordering': ordering,
        'form': form
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
        'tr_recs': sorted(tr_recs, key = lambda tutorial_resource: tutorial_resource.tutorial_detail.order),
        'ni_recs': NeedImprovementLog.objects.filter(tutorial_resource = tr_rec),
        'video_info': video_info,
        'media_url': settings.MEDIA_URL,
        'media_path': settings.MEDIA_ROOT,
        'tutorial_path': str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail_id) + '/',
        'script_base': settings.SCRIPT_URL
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
                row.status = 0
                row.save()
                add_contributor_notification(row, comp_title, 'This tutorial is unpublished for corrections.')
                messages.success(request, 'Tutorial unpublished successfully!')
                form = PublishToPending()
            except Exception as e:
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
            tutorials = TutorialResource.objects.filter(tutorial_detail_id__in = td_list, language_id = lang, status = 1).distinct().order_by('tutorial_detail__level_id', 'tutorial_detail__order')
            for tutorial in tutorials:
                data += '<option value = "' + str(tutorial.tutorial_detail.id) + '">' + tutorial.tutorial_detail.tutorial + '</option>'
            if data:
                data = '<option value = "">Select Tutorial</option>' + data
        elif foss:
            languages = Language.objects.filter(id__in = TutorialResource.objects.filter(tutorial_detail__in = TutorialDetail.objects.filter(foss_id = foss).values_list('id'), status = 1).values_list('language_id').distinct())
            for language in languages:
                data += '<option value = "' + str(language.id) + '">' + language.name + '</option>'
            if data:
                data = '<option value = "">Select Language</option>' + data

    return HttpResponse(json.dumps(data), content_type = 'application/json')


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
            except Exception as e:
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
            data = '<option value = "">Select Status</option><option value = "0">Pending</option>'
            if comp in ['outline', 'script', 'video']:
                compValue = getattr(tr_rec, comp + '_status')
            else:
                compValue = getattr(tr_rec.common_content, comp + '_status')
            if compValue:
                data += '<option value = "5">Need Improvement</option>'
            if comp in ['code', 'assignment', 'additional_material']:
                data += '<option value = "6">Not Required</option>'
        elif foss and lang:
            data = ['', '']
            td_list = TutorialDetail.objects.filter(foss_id = foss).values_list('id')
            lang_rec = Language.objects.get(pk = lang)
            tutorials = TutorialResource.objects.filter(tutorial_detail_id__in = td_list, language_id = lang, status = 0).distinct()
            data[0] = '<option value = "">Select Tutorial Name</option>'
            data[1] = '<option value = "outline">Outline</option><option value = "script">Script</option>'
            for tutorial in tutorials:
                data[0] += '<option value = "' + str(tutorial.tutorial_detail.id) + '">' + tutorial.tutorial_detail.tutorial + '</option>'
            if lang_rec.name == 'English':
                data[1] += '<option value = "slide">Slides</option><option value = "video">Video</option><option value = "code">Codefiles</option><option value = "assignment">Assignment</option><option value = "prerequisite">Prerequisite</option><option value = "keyword">Keywords</option><option value = "additional_material">Additional material</option>'
            else:
                data[1] += '<option value = "video">Video</option>'
            data[1] = '<option value = "">Select Component</option>' + data[1]
        elif foss:
            languages = Language.objects.filter(id__in = TutorialResource.objects.filter(tutorial_detail__in = TutorialDetail.objects.filter(foss_id = foss).values_list('id'), status = 0).values_list('language_id').distinct())
            for language in languages:
                data += '<option value = "' + str(language.id) + '">' + language.name + '</option>'
            if data:
                data = '<option value = "">Select Language</option>' + data

    return HttpResponse(json.dumps(data), content_type = 'application/json')


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
        and_query = None  # Query to search for a given term in each field
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
                # send email
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
                subject = "Reply: Missing Component Reply Notifications"
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
                    to = to, bcc = bcc, cc = cc,
                    headers = {'Reply-To': 'no-reply@spoken-tutorial.org', "Content-type": "text/html;charset = iso-8859-1"}
                )
                try:
                    result = email.send(fail_silently=False)
                except Exception as e:
                    print("*******************************************************")
                    print(message)
                    print("*******************************************************")
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
            form_data = form.save(commit = False)
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
            form_data = form.save(commit = False)
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
            form_data = form.save(commit = False)
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
                source_tutorial = TutorialDetail.objects.get(pk = form.cleaned_data['source_tutorial'], foss_id = form.cleaned_data['source_foss'])
                tcc = TutorialCommonContent.objects.get(tutorial_detail = source_tutorial)
                if int(form.cleaned_data['destination_tutorial']) == 0:
                    tcc.prerequisite_id = None
                    tcc.prerequisite_status = 6
                    messages.success(request, 'Prerequisite for <b>' + source_tutorial.tutorial + '</b> updated to <b>Not Required</b>')
                else:
                    destination_tutorial = TutorialDetail.objects.get(pk = form.cleaned_data['destination_tutorial'], foss_id = form.cleaned_data['destination_foss'])
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
            except Exception as e:
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
                foss = FossCategory.objects.get(pk = foss_id)
                language_id = request.POST.get('language')
                language = Language.objects.get(pk = language_id)
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
                messages.success(request, sheet_type.title()
                                 + 'sheet uploaded successfully!')
                form = UpdateSheetsForm()
            except Exception as e:
                print(e)
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
                foss = FossCategory.objects.get(pk = foss_id)
                language = Language.objects.get(pk = language_id)
                sheet_path = 'videos/' + str(foss.id) + '/' + \
                    foss.foss + '-' + sheet_type.title() + '-Sheet-' + \
                    language.name + '.pdf'
                if os.path.isfile(settings.MEDIA_ROOT + sheet_path):
                    data = '<a href = "' + settings.MEDIA_URL + sheet_path + \
                        '" target = "_blank"> Click here to view the currently \
                    available instruction sheet for the tutorial selected \
                    above</a>'
            except Exception as e:
                print(e)
                pass
        elif foss_id:
            tutorials = TutorialResource.objects.filter(
                Q(status = 1) | Q(status = 2),
                tutorial_detail__foss_id = foss_id
            ).values_list(
                'language_id',
                'language__name'
            ).order_by('language__name').distinct()
            for tutorial in tutorials:
                data += '<option value = "' + str(tutorial[0]) + '">' + \
                    str(tutorial[1]) + '</option>'
            if data:
                data = '<option value = "">-- Select Language --</option>' + data
    return HttpResponse(json.dumps(data), content_type = 'application/json')


@csrf_exempt
def ajax_get_tutorials(request):
    data = ''
    if request.method == 'POST':
        foss_id = request.POST.get('foss', '')
        if foss_id:
            tutorials = TutorialResource.objects.filter(
                Q(status = 1) | Q(status = 2),
                tutorial_detail__foss_id = foss_id
            ).values_list(
                'tutorial_detail_id',
                'tutorial_detail__tutorial'
            ).order_by('tutorial_detail__tutorial').distinct()
            for tutorial in tutorials:
                data += '<option value = "' + str(tutorial[0]) + '">' + \
                    str(tutorial[1]) + '</option>'
            if data:
                data = '<option value = "">-- Select Tutorial --</option>' + data
    return HttpResponse(json.dumps(data), content_type = 'application/json')


def view_brochure(request):
    template = 'creation/templates/view_brochure.html'
    my_dict = services.get_data_for_brochure_display()
    st_brochure = BrochureDocument.objects.filter(foss_course=36)
    pages = BrochurePage.objects.filter(brochure_id=st_brochure)
    st_pages=[]
    for page in pages:
        st_pages.append(page.page.url)


    context = {
        'my_dict': my_dict,
        'st_pages': st_pages
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
                foss = FossCategory.objects.get(pk = foss_id)

                tutorial_detail_id = request.POST.get('tutorial')
                tutorial = TutorialDetail.objects.get(pk = tutorial_detail_id)
                file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                file_name = tutorial.tutorial.replace(' ', '-') + '-Assignment' + file_extension
                file_path = settings.MEDIA_ROOT + 'videos/' + str(foss_id) + '/' + str(tutorial_detail_id) + '/resources/' + file_name

                fout = open(file_path, 'wb+')
                f = request.FILES['comp']
                # Iterate through the chunks.
                for chunk in f.chunks():
                    fout.write(chunk)
                fout.close()

                tr_res = TutorialResource.objects.get(tutorial_detail = tutorial_detail_id, language_id = 22)
                tr_res.common_content.assignment = file_name
                tr_res.common_content.assignment_status = 4
                tr_res.common_content.assignment_user = request.user
                tr_res.common_content.save()

                messages.success(request, 'Assignment updated successfully!')
                form = UpdateAssignmentForm()
            except Exception as e:
                print(e)
    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/update_assignment.html', context)


@login_required
def update_codefiles(request):
    if not is_administrator(request.user):
        raise PermissionDenied()
    form = UpdateCodefilesForm()
    if request.method == 'POST':
        form = UpdateCodefilesForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                foss_id = request.POST.get('foss')
                foss = FossCategory.objects.get(pk = foss_id)

                tutorial_detail_id = request.POST.get('tutorial')
                tutorial = TutorialDetail.objects.get(pk = tutorial_detail_id)
                file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                file_name = tutorial.tutorial.replace(' ', '-') + '-Codefiles' + file_extension
                file_path = settings.MEDIA_ROOT + 'videos/' + str(foss_id) + '/' + str(tutorial_detail_id) + '/resources/' + file_name

                fout = open(file_path, 'wb+')
                f = request.FILES['comp']
                # Iterate through the chunks.
                for chunk in f.chunks():
                    fout.write(chunk)
                fout.close()

                tr_res = TutorialResource.objects.get(tutorial_detail = tutorial_detail_id, language_id = 22)
                tr_res.common_content.code = file_name
                tr_res.common_content.code_status = 4
                tr_res.common_content.code_user = request.user
                tr_res.common_content.save()

                messages.success(request, 'Codefiles updated successfully!')
                form = UpdateCodefilesForm()
            except Exception as e:
                print(e)
    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/update_codefiles.html', context)

@login_required
def update_common_component(request):
    #for codefiles, slides and additional material
    if not is_administrator(request.user):
        raise PermissionDenied()
    form = UpdateCommonCompForm()
    if request.method == 'POST':
        form = UpdateCommonCompForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                foss_id = request.POST.get('foss')
                foss = FossCategory.objects.get(pk=foss_id)

                common_comp = request.POST.get('component_type')

                tutorial_detail_id = request.POST.get('tutorial')
                tutorial = TutorialDetail.objects.get(pk=tutorial_detail_id)
                file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                file_name =  tutorial.tutorial.replace(' ', '-') + '-'+common_comp + file_extension
                file_path = settings.MEDIA_ROOT + 'videos/' + str(foss_id) + '/' + str(tutorial_detail_id) + '/resources/' + file_name

                fout = open(file_path, 'wb+')
                f = request.FILES['comp']
                # Iterate through the chunks.
                for chunk in f.chunks():
                    fout.write(chunk)
                fout.close()

                tr_res = TutorialResource.objects.get(tutorial_detail=tutorial_detail_id, language_id = 22)
                if common_comp == 'Codefiles':
                    tr_res.common_content.code = file_name
                    tr_res.common_content.code_status = 4
                    tr_res.common_content.code_user = request.user
                if common_comp == 'Slides':
                    tr_res.common_content.slide = file_name
                    tr_res.common_content.slide_status = 4
                    tr_res.common_content.slide_user = request.user
                if common_comp == 'Additionalmaterial':
                    tr_res.common_content.additional_material = file_name
                    tr_res.common_content.additional_material_status = 4
                    tr_res.common_content.additional_material_user = request.user
                tr_res.common_content.save()



                messages.success(request, common_comp+' updated successfully!')
                form = UpdateCommonCompForm()
            except Exception as e:
                print(e)
    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/update_common_comp.html', context)
# -------------- Bidding Module -----------------

@csrf_exempt
@login_required
def rate_contributors(request):

    # Check if Language Manager for this request
    if not is_language_manager(request.user):
        raise PermissionDenied()
    data = "Response"
    context = {}
    user_id = request.POST.get('user_id')
    lang_select = request.POST.get('language')
    new_rating = request.POST.get('rating')
    mode = request.POST.get('mode')
    if mode == 'update':
        user_obj = User.objects.get(id = user_id)
        lang = Language.objects.get(name = lang_select)
        contributor_rating = ContributorRating.objects.filter(
            user = user_obj, language_id = lang)
        if contributor_rating.exists():
            contributor_rating.update(rating = new_rating)
        else:
            contributor_rating = ContributorRating()
            contributor_rating.language = lang
            contributor_rating.rating = new_rating
            contributor_rating.user = user_obj
            contributor_rating.save()
        messages.success(request, 'Ratings Saved Successfully')
        return HttpResponse(json.dumps(data), content_type = 'application/json')


    if lang_select == '':
        messages.error(request,"Please filter a language")
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    else:

        lang_qs = \
            Language.objects.filter(id__in = LanguageManager.objects.filter(user = request.user,
                                                                          status = STATUS_DICT['active']).values('language'))
        header = {
                1: SortableHeader('Check', False),
                2: SortableHeader('user__username', True, 'User'),
                3: SortableHeader('language', False, 'Language'),
                4: SortableHeader('rating', False, 'Rating'),
                5: SortableHeader('Action', False, ),
            }

        raw_get_data = request.POST.get('o', None)
        rated_contributors = ContributorRating.objects.filter(
            language_id = lang_select).values('user__id',
            'user__username', 'rating','language__name').order_by('-rating')

        context['rated_contributors'] = rated_contributors
        tutorials_sorted = get_sorted_list(request, rated_contributors,
                        header, raw_get_data)
        contributors_sorted = get_sorted_list(request, rated_contributors,
                        header, raw_get_data)
        ordering = get_field_index(raw_get_data)
        contributor_list = ContributorRatingFilter(request.POST,
            queryset = tutorials_sorted)
        form = contributor_list.form
        if lang_qs:
            form.fields['language'].queryset = lang_qs
        context['form'] = form
        context['header'] = header
        context['contributors'] = contributors_sorted

        context['ordering'] = ordering



        context.update(csrf(request))
        return render(request, 'creation/templates/rate_contributors.html',
                      context)


def add_contributorrating(role_request):
        contributor_with_rating = \
            ContributorRating.objects.filter(user_id = role_request.user_id,
                                       language_id = role_request.language_id)
        if not contributor_with_rating.exists():
            new_role_request = ContributorRating()
            new_role_request.user_id = role_request.user_id
            new_role_request.language_id = role_request.language_id
            new_role_request.save()


@login_required
@csrf_protect
def allocate_tutorial(request, sel_status, role):
    context = {}
    global global_req
    global_req = request
    user = User.objects.get(id = request.user.id)
    if not (user.is_authenticated() and
        (is_contributor(user) or is_language_manager(request.user)
            or is_administrator(request.user))):
        raise PermissionDenied()

    active = sel_status
    final_query = None
    fosses = []
    final_query = ''
    bid_count = 0
    tutorials_count = 0

    if is_language_manager(request.user) and role == 'language_manager':
        lang_qs = Language.objects.filter(
            id__in = LanguageManager.objects.filter(user = request.user,
            status = STATUS_DICT['active']).values('language'))

    else:
        lang_qs = Language.objects.filter(id__in = RoleRequest.objects.filter(
            Q(role_type = ROLES_DICT['contributor'])|Q(role_type = ROLES_DICT['external-contributor']),
            user = request.user , status = STATUS_DICT['active']).values('language'))


    if sel_status == 'completed':
        header = {
            1: SortableHeader('# ', False),
            2: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
            3: SortableHeader('Tutorial', False),
            4: SortableHeader('language__name', False, 'Language'),
            5: SortableHeader('created', False, 'Date Created'),
            6: SortableHeader('script_user_id', False, 'Script user'),
            7: SortableHeader('video_user_id', False, 'Video user'),
        }

        if is_language_manager(request.user):
            final_query = TutorialResource.objects.filter(
                status = PUBLISHED, language__in = lang_qs).order_by('-updated')
        else:
            final_query = TutorialResource.objects.filter(
                Q(script_user_id = request.user.id)|Q(video_user_id = request.user.id),
                status = PUBLISHED).order_by('-updated')
        bid_count = final_query.aggregate(Count('id'))
    elif sel_status == 'available':

        header = {
            1: SortableHeader('Tutorial Level', False),
            2: SortableHeader('Order Id', False),
            3: SortableHeader('Tutorial', False),
            4: SortableHeader('language__name', True, 'Language'),
            5: SortableHeader('Days', False),
            6: SortableHeader('Bid', False),
        }

        status = 4
        final_query = TutorialsAvailable.objects.filter(
            language__in = lang_qs).order_by('tutorial_detail__foss__foss',
            'tutorial_detail__level', 'language','tutorial_detail__order'   )

    elif sel_status == 'ongoing':
        if is_language_manager(request.user) and role == 'language_manager':
            header = {
                1: SortableHeader('# ', False),
                2: SortableHeader('tutorial_detail__level', True, 'Tutorial Level'),
                3: SortableHeader('tutorial_detail__order', True, 'Order Id'),
                4: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
                5: SortableHeader('Tutorial', False),
                6: SortableHeader('language__name', False, 'Language'),
                7: SortableHeader('script_user_id', True, 'Script User'),
                8: SortableHeader('video_user_id', True, 'Video User'),
                9: SortableHeader('tutorial_detail_id__tutorialresource__updated', True, 'Bid Date'),
                10: SortableHeader('submissiondate', True,
                                  'Submission Date'),
                11: SortableHeader('extension_status', True, 'Extension'),
                12: SortableHeader('Revoke ', False),
                13: SortableHeader('Edit User',False)
            }
        else:
            header = {
                1: SortableHeader('# ', False),
                2: SortableHeader('tutorial_detail__level', True, 'Tutorial Level'),
                3: SortableHeader('tutorial_detail__order', True, 'Order Id'),
                4: SortableHeader('tutorial_detail__foss__foss', True, 'FOSS Course'),
                5: SortableHeader('Tutorial', False),
                6: SortableHeader('language__name', False, 'Language'),
                7: SortableHeader('script_user_id', False, 'Script user'),
                8: SortableHeader('video_user_id', False, 'Video user'),
                9: SortableHeader('tutorial_detail_id__tutorialresource__updated', True, 'Bid Date'),
                10: SortableHeader('submissiondate', True, 'Submission Date'),
                11: SortableHeader('extension_status', True, 'Extension' ),
            }


        tutorialresource_assigned =  get_assigned_tutorials(request,user.id,lang_qs)
        final_query = tutorialresource_assigned.order_by(
                'tutorial_detail__foss__foss', 'language__name', 'tutorial_detail__order')

    else:
        messages.error(request,"Invalid request. Please try again !!!")

    extension = []
    pub_tutorials_set = final_query
    context['datetoday'] = datetime.now()
    raw_get_data = request.POST.get('o', None)
    tutorials_sorted = get_sorted_list(request, pub_tutorials_set,
                                       header, raw_get_data)

    ordering = get_field_index(raw_get_data)
    tutorials = CreationStatisticsFilter(request.POST,
                                         queryset = tutorials_sorted)

    tutorials_count = TutorialsAvailable.objects.filter(
            language__in = lang_qs).aggregate(Count('id'))

    if sel_status in ('available','ongoing'):
        bid_count = tutorials.qs.count()
        context['bid_count__count'] = bid_count

    try:
        if sel_status == 'completed':
            tutorials_count = bid_count['id__count'] + tutorials_count['id__count']
            context['tutorials_count'] = tutorials_count
            context['bid_count__count'] = bid_count['id__count']
            context['perc'] = bid_count['id__count'] * 100 \
                / tutorials_count
        else:
            context['tutorials_count'] = tutorials_count['id__count']
            context['perc'] = bid_count * 100 \
                / tutorials_count['id__count']

    except ZeroDivisionError:
        context['bid_count__count'] = 0
        context['perc'] = 0


    form = tutorials.form
    if lang_qs:
        form.fields['language'].queryset = lang_qs

    if request.method == 'POST':
        language_id = request.POST.get('language')
        script_user = request.POST.get('script_user')
        video_user = request.POST.get('video_user')
        context['foss_list'] = foss_list(script_user, video_user, language_id)
        if language_id:
            contributors_list = User.objects.filter(id__in = active_contributor_list([int(language_id)]))
            rated_contributors = ContributorRating.objects.filter(rating__gt = 0,
                language_id = language_id, user_id__in = contributors_list
                )
            context['contributors'] = rated_contributors.values_list('user_id', 'user__username', 'rating')
            # Update script & video user as per language choice
            # This will show contributors as per the language selection
            form.fields['script_user'].queryset =  contributors_list
            form.fields['video_user'].queryset = contributors_list
        else:
            contributors_list = User.objects.filter(id__in = active_contributor_list(lang_qs))
            # This will show all contributors under the language manager
            if contributors_list:
                form.fields['script_user'].queryset = contributors_list
                form.fields['video_user'].queryset = contributors_list

    else:
    	contributors_list = User.objects.filter(id__in = active_contributor_list(lang_qs))
    	# This will show all contributors under the language manager
    	if contributors_list:
    		form.fields['script_user'].queryset = contributors_list
    		form.fields['video_user'].queryset = contributors_list

    context['form'] = form

    # Pagination
    paginator = Paginator(tutorials.qs, 50)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context['collection'] = posts
    context['header'] = header
    context['ordering'] = ordering
    context['status'] = active
    context['counter'] = itertools.count(1)
    context['is_administrator'] = is_administrator(request.user)

    context.update(csrf(request))
    if role == 'language_manager':
	    if is_language_manager(request.user) or is_administrator(request.user):
	        return render(request,
	                      'creation/templates/allocate_tutorial_manager.html', context)
    elif role == 'contributor':
        return render(request,
                      'creation/templates/allocate_tutorial.html',
                      context)
def foss_list(script_user,video_user, language_id):
    foss_list = TutorialResource.objects.none()
    if script_user and video_user:
        foss_list = TutorialResource.objects.filter(
            script_user_id = script_user, video_user_id = video_user,
            status = UNPUBLISHED,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned']
            )
    elif script_user:
        foss_list = TutorialResource.objects.filter(
            script_user_id = script_user, status = UNPUBLISHED,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned']
            )
    elif video_user:
        foss_list = TutorialResource.objects.filter(
            video_user_id = video_user,status = UNPUBLISHED,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned']
            )
    if language_id :
        foss_list=foss_list.filter(language_id = int(language_id))
    return foss_list.exclude(language_id=22
        ).order_by('language_id').values('tutorial_detail__foss__foss','language__name').distinct()


def active_contributor_list(language_id):
    contributors_updated = RoleRequest.objects.filter(
    Q(role_type = ROLES_DICT['contributor'])|Q(role_type = ROLES_DICT['external-contributor']),
    status = STATUS_DICT['active'], language_id__in = language_id).values_list('user__id').distinct()
    return contributors_updated

@csrf_exempt
def get_rated_contributors(request):
    language_id = request.POST.get('language')
    contributors_updated = active_contributor_list([int(language_id)])

    rated_contributors = ContributorRating.objects.filter(rating__gt = 0,
        language_id = language_id, user_id__in = contributors_updated
        ).values_list('user_id', 'user__username', 'rating')
    data = ""
    for contributor in rated_contributors:
        if contributor[2]<=3:
            data = data + '<option id='+str(contributor[0])+' style="color:red" >' + contributor[1]+ '</option>'
        else:
            data = data + '<option id='+str(contributor[0])+' style="color:green" >' + contributor[1]+ '</option>'
    return HttpResponse(json.dumps(data), content_type = 'application/json')



@csrf_exempt
def update_contributors(request):
    try:
        tutorial_resource_id = request.POST.get('tr_id')
        if tutorial_resource_id is not 'None':
            script_user_id = request.POST.get('script_user')
            video_user_id = request.POST.get('video_user')
            tutorial_resource = TutorialResource.objects.get(id = tutorial_resource_id)

            script_user_foss_count = no_of_foss_gt_4(request,
                script_user_id, tutorial_resource.tutorial_detail_id, tutorial_resource.language.id)

            video_user_foss_count = no_of_foss_gt_4(request,
                video_user_id, tutorial_resource.tutorial_detail_id, tutorial_resource.language.id)
            script_user_bid_count = TutorialResource.objects.filter(script_user_id = script_user_id,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned'] , status = UNPUBLISHED)

            video_user_bid_count = TutorialResource.objects.filter(video_user_id = video_user_id,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned'] , status = UNPUBLISHED)

            data = "Updated"

            update_to_script_user = True
            update_to_video_user = True

            if not script_user_foss_count :
                if contributor_rating_less_than_3(request ,script_user_id , tutorial_resource.language):
                    if not bid_count_less_than_3(script_user_id,
                        tutorial_resource.tutorial_detail_id, tutorial_resource.language_id):
                        update_to_script_user = False
                        messages.error(request, 'You cannot allocate more than 3 tutorials to a contributor of rating less than 3. <i>Error at Script User </i>')
            else:
                update_to_script_user = False
            if not video_user_foss_count :
                if contributor_rating_less_than_3(request ,video_user_id , tutorial_resource.language):
                    if not bid_count_less_than_3(video_user_id,
                        tutorial_resource.tutorial_detail_id, tutorial_resource.language_id):
                        update_to_video_user = False
                        messages.error(request, 'You cannot allocate more than 3 tutorials to a contributor of rating less than 3. <i>Error at Video User </i>')
            else:
                update_to_video_user = False

            if update_to_script_user and update_to_video_user:
                if tutorial_resource.script_user_id != script_user_id:
                    add_tutorial_contributor_notification(tutorial_resource.script_user_id,
                        tutorial_resource.id, 'revoke')
                    revoke_contributor_role(tutorial_resource.tutorial_detail_id,
                        tutorial_resource.language_id , tutorial_resource.script_user_id)

                if tutorial_resource.script_user_id != script_user_id:
                    add_tutorial_contributor_notification(tutorial_resource.video_user_id,
                        tutorial_resource.id, 'revoke')
                    revoke_contributor_role(tutorial_resource.tutorial_detail_id,
                        tutorial_resource.language_id , tutorial_resource.video_user_id)


                add_or_update_contributor_role(tutorial_resource.tutorial_detail , tutorial_resource.language_id , script_user_id)
                add_tutorial_contributor_notification(script_user_id, tutorial_resource.id, 'add')
                add_or_update_contributor_role(tutorial_resource.tutorial_detail , tutorial_resource.language_id , video_user_id)
                add_tutorial_contributor_notification(video_user_id, tutorial_resource.id, 'add')

                tutorial_resource.script_user = User.objects.get(id = script_user_id)
                tutorial_resource.video_user = User.objects.get(id = video_user_id)
                tutorial_resource.save()
                messages.success(request, 'Updated')
        else:
            messages.error(request,"Invalid request")
        return HttpResponse(json.dumps(data), content_type = 'application/json')
    except Exception as e:
        print (e)

def get_assigned_tutorials(request , user_id , language_set):
    if is_language_manager(request.user):
        tutorialresource_assigned = TutorialResource.objects.filter(
            language__in = language_set, status = UNPUBLISHED,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned']
            ).exclude(language_id = 22)
    else:
        tutorialresource_assigned = TutorialResource.objects.filter(
            Q(video_user = user_id)|Q(script_user = user_id),
            language__in = language_set , status = UNPUBLISHED,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned']
            ).exclude(language_id = 22)
    return tutorialresource_assigned

PUBLISHED = 1

@login_required
def refresh_tutorials(request, tut_resource):
    count = 0
    if tut_resource.language.id == 22 :
        tutorials = TutorialDetail.objects.filter(foss__is_translation_allowed = 1,
            id__in = TutorialResource.objects.filter(id = tut_resource.id ,status = PUBLISHED,
            language = 22).values('tutorial_detail').distinct())
        if is_administrator(request.user) or is_qualityreviewer(request.user):
            lang_qs = Language.objects.all()
        else:
            raise PermissionDenied()
        for tutorial in tutorials:
            for a_lang in lang_qs:
                this_tutorial_user_lang = TutorialResource.objects.filter(Q(
                    status = PUBLISHED)|Q(
                    assignment_status = ASSIGNMENT_STATUS_DICT['assigned']),
                    tutorial_detail = tutorial, language = a_lang
                    )
                if not this_tutorial_user_lang.exists():
                    add_to_tutorials_available(tutorial,a_lang)
                    messages.success(request, tutorial.tutorial + ' added for ', a_lang.name)
    return True

def add_to_tutorials_available(tutorial,language):
    tutorialsavailable = TutorialsAvailable.objects.filter(
    tutorial_detail = tutorial, language = language)
    if not tutorialsavailable.exists():
        tutorialsavailable = TutorialsAvailable()
        tutorialsavailable.tutorial_detail = tutorial
        tutorialsavailable.language = language
        tutorialsavailable.save()

UNPUBLISHED = 0

def no_of_foss_gt_4(request ,user, tut_id, language_id):

    this_tut = TutorialDetail.objects.get(id = tut_id)
    foss_id = this_tut.foss.id
    # To give language manager the privileges to assign any no of foss
    if is_administrator(request.user):
        return False
    else:
        all_foss = TutorialResource.objects.filter(
            Q(script_user_id = user) | Q(video_user_id = user),
            language_id = int(language_id),status = UNPUBLISHED,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned']
            )
        list_count = all_foss.values('tutorial_detail__foss','language_id').distinct().count()
        check = all_foss.filter(tutorial_detail__foss_id=foss_id, language_id=language_id).exists()
        if check:
            return False
        else:
            if list_count >= 4:
                messages.error(request, 'Maximum of 4 FOSSes allowed per user')
                return True
            return False
        return False

LEVEL_NAME = {1: 'Basic', 2: 'Intermediate', 3: 'Advanced'}
SUPER_ADMIN_USER_ID = 7
def disallow(request , lower_level,tut):
    level_name_in_words = LEVEL_NAME[lower_level]
    messages.error(request, str(level_name_in_words) +
        ' level of ' + str(tut.foss) +' is available. Please complete it first.')

def add_or_update_contributor_role(tutorial_detail , language_id , user_id):
    contributor_role = ContributorRole.objects.filter(
        tutorial_detail_id = tutorial_detail.id,
        language_id = language_id,
        user_id = user_id)

    # Update data in Contributor Role
    if contributor_role.exists():
        contributor_role = contributor_role.update(status = STATUS_DICT['active'])

    else:
        contributor_create = ContributorRole()
        contributor_create.foss_category_id = tutorial_detail.foss_id
        contributor_create.language_id = language_id
        contributor_create.status = STATUS_DICT['active']
        contributor_create.user_id = user_id
        contributor_create.tutorial_detail_id = tutorial_detail.id
        contributor_create.save()

def add_tutorial_contributor_notification(user_id, tuto_resource_id, message_type):

    tutorial_resource = TutorialResource.objects.get(id = tuto_resource_id)
    comp_title = tutorial_resource.tutorial_detail.foss.foss + ': ' + \
        tutorial_resource.tutorial_detail.tutorial + ' - ' + tutorial_resource.language.name
    if message_type == 'add':
        message = "Submission date is :"+str(datetime.date(tutorial_resource.submissiondate))
    elif message_type == 'revoke':
        message = "The tutorial is revoked from you"
    elif message_type == 'extend':
        message = "Submission date is extended to :"+str(datetime.date(tutorial_resource.submissiondate))

    try:

        contributor_notification = ContributorNotification.objects.filter(
            user_id = user_id , tutorial_resource = tutorial_resource )

        if contributor_notification.exists():
            contributor_notification.update(message = message, created = datetime.now())
        else:
            ContributorNotification.objects.create(user_id = user_id , title = comp_title,
                message = message , tutorial_resource_id = tutorial_resource.id)
    except Exception as e:
        print (e)


@login_required
def single_tutorial_allocater(request, tut, lid, days, user):
    # If timezone issue is solved, + 1 can be removed
    if days != 1:
        submissiondate = datetime.date(timezone.now() +
                                       timezone.timedelta(days = int(days) + 1))
    tutorial_resource = TutorialResource.objects.filter(
        tutorial_detail_id = tut.id,
        language_id = lid)

    # Add a role in the COntributor Role table for the Tutorial
    add_or_update_contributor_role(tut, lid , user.id)

    # Update data in Tutorial Resource
    if tutorial_resource.exists():
        tutorial_resource = tutorial_resource.update(outline_user = user,
            script_user = user, video_user = user,
            submissiondate = submissiondate,
            assignment_status = ASSIGNMENT_STATUS_DICT['assigned'])
        messages.warning(request, 'Successfully updated ' +
                        tut.tutorial + ' to ' + str(user) + ' : ' +
                         str(submissiondate))

    else:
        common_content = TutorialCommonContent.objects.get(tutorial_detail_id = tut.id)
        tutorial_resource = TutorialResource()
        tutorial_resource.tutorial_detail_id = tut.id
        tutorial_resource.language_id = lid
        tutorial_resource.common_content_id = common_content.id
        tutorial_resource.outline_user = user
        tutorial_resource.script_user = user
        tutorial_resource.video_user = user
        # assignment_status -
        # 0 : Not Assigned , 1 : Work in Progress , 2 : Completed
        tutorial_resource.assignment_status = ASSIGNMENT_STATUS_DICT['assigned']
        tutorial_resource.submissiondate = submissiondate
        tutorial_resource.save()

        messages.success(request, 'Successfully alloted ' +
                         tut.tutorial + ' to ' + str(user) + ' : ' +
                         str(submissiondate))

    tutorial_resource = TutorialResource.objects.filter(
        tutorial_detail_id = tut.id,
        language_id = lid)
    tutorial_resource_id = tutorial_resource.values_list('id')
    # Add a Contributor Notification for this tutorial
    if tutorial_resource_id:
        add_tutorial_contributor_notification(user.id, tutorial_resource_id, 'add')

    # Super admin should be able to see the super admin language tutorials atleast
    super_admin_contributor_languages = RoleRequest.objects.filter(role_type = 0,
        user_id=SUPER_ADMIN_USER_ID, status = STATUS_DICT['active'], language_id = lid).values(
        'language').distinct()

    tutorial_resource = TutorialResource.objects.filter( tutorial_detail =tut,
        language_id__in = super_admin_contributor_languages)

    tutorialsavailableobj = TutorialsAvailable.objects.filter(
                tutorial_detail = tut, language = lid)
    if tutorialsavailableobj.exists():
        tutorialsavailableobj.delete()
    else:
        # The only purpose over here is to remove from available tutorials if it exists
        pass

    for tutorial in tutorial_resource:
        super_admin_contrib_roles = ContributorRole.objects.filter(
        user_id = SUPER_ADMIN_USER_ID, language_id = tutorial.language,
        tutorial_detail_id = tutorial.tutorial_detail)

        if not super_admin_contrib_roles.exists():
            add_previous_contributor_role = ContributorRole()
            add_previous_contributor_role.foss_category_id = tutorial.tutorial_detail.foss_id
            add_previous_contributor_role.language_id = tutorial.language_id
            add_previous_contributor_role.user_id = SUPER_ADMIN_USER_ID
            add_previous_contributor_role.status = STATUS_DICT['active']
            add_previous_contributor_role.tutorial_detail_id = tutorial.tutorial_detail_id
            add_previous_contributor_role.save()

    return True

def contributor_rating_less_than_3(request, uid , language):
    contributor_rating = ContributorRating.objects.filter(
        user_id = uid,language = language).values('rating', 'language__name')
    if contributor_rating[0]['rating'] <= 3:
        return True
    else:
        return False

def bid_count_less_than_3(uid, tutorial_detail_id, language_id):

    bid_count = TutorialResource.objects.filter(Q(script_user_id = uid) | Q(video_user_id = uid),
        assignment_status = ASSIGNMENT_STATUS_DICT['assigned'] , status = UNPUBLISHED
        ).exclude(language_id = 22).values('tutorial_detail_id','language_id')
    list_count = list({(int(v['tutorial_detail_id']),int(v['language_id'])) for v in bid_count})

    if (int(tutorial_detail_id),int(language_id)) in list_count:
        return True
    else:
        if len(list_count) >= 3:
            return False
        return True

@login_required
@csrf_exempt
def allocate(request, tdid, lid, uid, days):
    # Data is being passed from another function
    # hence the below get functions need not be in try catch
    try:
        user = User.objects.get(id = uid)
        tut = TutorialDetail.objects.get(id = tdid)
    except (User.DoesNotExist , TutorialDetail.DoesNotExist):
        messages.error(request,"Invalid data . Please try again !!! ")
        raise
    data = 'Response'
    this_language = Language.objects.get(id = lid)
    contributor_rating = ContributorRating.objects.filter( rating__gt = 0,
        user_id = uid,language = this_language).values('rating', 'language__name')
    if not contributor_rating.exists():
        messages.error(request,
                "According to our new system, you are not enabled for " + str(this_language) +
                ". Please contact your Language Manager")

        return HttpResponse(json.dumps(data), content_type = 'application/json')


    try:
        final_query =  TutorialsAvailable.objects.get(tutorial_detail_id = tut.id,language = lid)
        if not no_of_foss_gt_4(request,uid, tdid, lid):
            all_lower_tutorials = TutorialDetail.objects.filter(foss_id = final_query.tutorial_detail.foss_id,
                level_id = final_query.tutorial_detail.level_id - 1).values('id')
            lower_tutorial_level = TutorialsAvailable.objects.filter(tutorial_detail_id__in = all_lower_tutorials ,
                                                                    language = lid).values('tutorial_detail_id__level').distinct()
            if contributor_rating_less_than_3(request ,uid , this_language):
                if bid_count_less_than_3(uid, tdid, lid):
                    if lower_tutorial_level.exists():
                        disallow( request,lower_tutorial_level[0]['tutorial_detail_id__level'], tut)
                    else:
                        single_tutorial_allocater(request, tut, lid, days, user)
                else:
                    if is_language_manager(request.user):
                        messages.error(
                            request,'You cannot allocate more than 3 tutorials to a contributor of rating less than 3')
                    else:
                        messages.error(request, 'You cannot allocate more than 3 tutorials ')
                return HttpResponse(json.dumps(data),
                                    content_type = 'application/json')
            else:
                if lower_tutorial_level.exists():
                    disallow(request ,lower_tutorial_level[0]['tutorial_detail_id__level'], tut)
                else:
                    single_tutorial_allocater(request, tut, lid, days, user)


    except Exception as e:
        raise e

    return HttpResponse(json.dumps(data), content_type = 'application/json')


@login_required
@csrf_exempt
def extend_submission_date(request):
    tutorial = request.POST.get('tutorial')
    data = 'Extended'
    try:
        tutorial_resource = TutorialResource.objects.get(id = tutorial)
        if tutorial_resource.extension_status >= 1:
            messages.error(request,
                           'You have exceeded the no of extensions')
        else:
            tutorial_resource.submissiondate = \
                datetime.date(datetime.now() + timedelta(days = 3))
            tutorial_resource.extension_status += 1
            tutorial_resource.save()
            add_tutorial_contributor_notification(tutorial_resource.script_user_id,
                tutorial_resource.id, 'extend')
            add_tutorial_contributor_notification(tutorial_resource.video_user_id,
                tutorial_resource.id, 'extend')
            messages.success(request,'Extended')
    except TutorialResource.DoesNotExist:
        # Here the error can only occur when the tutorial resource entry is not found.
        messages.error(request,
                       'Some Internal error. Please contact the Technical Team'
                       )

    return HttpResponse(json.dumps(data),
                        content_type = 'application/json')


@login_required
def allocate_foss(request, fid, lang, uid, level, days):

    language = Language.objects.get(name = lang)
    contrib = ContributorRating.objects.filter(user_id = uid,
                                               language = language).values('rating')

    user = User.objects.get(id = uid)
    data = 'Response'
    tdids = TutorialDetail.objects.filter(foss_id = fid,level__level = level).order_by('order').values('id')
    tdid_available = TutorialsAvailable.objects.filter(
                tutorial_detail_id__in = tdids,language = language).order_by(
                'tutorial_detail__level','tutorial_detail__order')

    for a_tdid_available in tdid_available:
        allocate(request,a_tdid_available.tutorial_detail.id,
            language.id,
            user.id,
            days)

    return HttpResponse(json.dumps(data), content_type = 'application/json')

def revoke_contributor_role(tutorial_detail_id , language_id , user_id):
    revoke_contributor_role = ContributorRole.objects.filter(
            user_id = user_id, language_id = language_id ,
            tutorial_detail_id = tutorial_detail_id)

    if revoke_contributor_role.exists():
        revoke_contributor_role.update(status = STATUS_DICT['inactive'])
    else:
        print ("Error")
        pass
    return True

@csrf_exempt
def revoke_allocated_tutorial(request):
    data = 'Response'
    try:
        tutorial_resource_id = request.POST.get('tutorial_resource_id')
        tutorialresource_to_revoke = TutorialResource.objects.get(id = tutorial_resource_id)
        tutorialresource_to_revoke.assignment_status = ASSIGNMENT_STATUS_DICT['un-assigned']
        tutorialresource_to_revoke.save()

        language_id = tutorialresource_to_revoke.language_id
        tutorial_detail_id = tutorialresource_to_revoke.tutorial_detail_id


        revoke_contributor_role(tutorial_detail_id , language_id , tutorialresource_to_revoke.script_user_id)
        revoke_contributor_role(tutorial_detail_id , language_id , tutorialresource_to_revoke.video_user_id)
        reason = request.POST.get('submissiondate_message') # If submission date checkbox is checked
        # if reason:
        #     message = "You have delayed the submission, hence the tutorial is revoked from you."
        #     send_mail_to_contributor(tutorialresource_to_revoke.script_user_id, tutorial_detail_id, language_id, reason)
        #     send_mail_to_contributor(tutorialresource_to_revoke.video_user_id, tutorial_detail_id, language_id, reason)

        tutorialsavailable = TutorialsAvailable.objects.filter(
            tutorial_detail_id = tutorial_detail_id , language_id = language_id)
        if tutorialsavailable.exists():
            tutorialsavailable.update(tutorial_detail_id = tutorial_detail_id,
                                         language_id = language_id)
        else:
            tutorialsavailable = TutorialsAvailable()
            tutorialsavailable.language_id = language_id
            tutorialsavailable.tutorial_detail_id = tutorial_detail_id
            tutorialsavailable.save()


    except Exception as e:
        raise e
    try:
        # Check user notification exists
        if tutorialresource_to_revoke.script_user_id != tutorialresource_to_revoke.video_user_id:
            add_tutorial_contributor_notification(tutorialresource_to_revoke.script_user_id,
                tutorialresource_to_revoke.id, 'revoke')

            add_tutorial_contributor_notification(tutorialresource_to_revoke.video_user_id,
                tutorialresource_to_revoke.id, 'revoke')
        else:
            add_tutorial_contributor_notification(tutorialresource_to_revoke.script_user_id,
                tutorialresource_to_revoke.id, 'revoke')

    except Exception as e:
        raise e

    tutorialresource_to_revoke.assignment_status = STATUS_DICT['inactive']
    tutorialresource_to_revoke.save()

    messages.success(request, 'Tutorial Revoked')
    return HttpResponse(json.dumps(data), content_type = 'application/json')


@csrf_exempt
def get_languages(request, uid):
    data = '<option> --- Select a Language ---  </option>'

    lang_qs = \
        Language.objects.filter(id__in = RoleRequest.objects.filter(
            user_id = uid,status = 1,role_type = ROLES_DICT['contributor']
            ).values('language')).values_list('id', 'name')
    for a_lang in lang_qs:
        data += '<option value = ' + str(a_lang[0]) + '>' \
            + str(a_lang[1]) + '</option>'
    return HttpResponse(json.dumps(data),
                        content_type = 'application/json')

@csrf_exempt
def get_domain_languages(request, uid):
    data = '<option> --- Select a Language ---  </option>'

    lang_qs = \
        Language.objects.filter(id__in = RoleRequest.objects.filter(
            user_id = uid,status = 1,role_type = ROLES_DICT['domain-reviewer']
            ).values('language')).values_list('id', 'name')

    for a_lang in lang_qs:
        data += '<option value = ' + str(a_lang[0]) + '>' \
            + str(a_lang[1]) + '</option>'
    return HttpResponse(json.dumps(data),
                        content_type = 'application/json')

@csrf_exempt
def get_quality_languages(request, uid):
    data = '<option> --- Select a Language ---  </option>'

    lang_qs = \
        Language.objects.filter(id__in = RoleRequest.objects.filter(
            user_id = uid,status = 1,role_type = ROLES_DICT['quality-reviewer']
            ).values('language')).values_list('id', 'name')

    for a_lang in lang_qs:
        data += '<option value = ' + str(a_lang[0]) + '>' \
            + str(a_lang[1]) + '</option>'
    return HttpResponse(json.dumps(data),
                        content_type = 'application/json')

@csrf_exempt
def get_tutorials(request, fid, lang):
    level = {1: '(B)', 2: '(I)', 3: '(A)'}
    data = '<option> --- Select a Tutorial ---  </option>'
    if int(lang) == 22:
        tuto_available = TutorialDetail.objects.filter(
            foss_id=fid).values_list('id','tutorial','level').order_by('level')
    else:
        tuto_available = TutorialsAvailable.objects.filter(
            language=lang, tutorial_detail_id__in = TutorialDetail.objects.filter(
            foss_id = int(fid)).order_by('level').values('id')
            ).distinct().values_list('tutorial_detail_id',
            'tutorial_detail_id__tutorial', 'tutorial_detail__level')

    for a_tutorial in tuto_available:
        data += '<option value = ' + str(a_tutorial[0]) + '>' \
            + str(a_tutorial[1]) + ' ' + str(level[a_tutorial[2]]) \
            + '</option>'
    return HttpResponse(json.dumps(data),
                        content_type = 'application/json')


# Languages other than the Contributor's Language/s
@csrf_exempt
def get_other_languages(request, uid):
    data = '<option> --- Select a Language ---  </option>'
    lang_qs = \
        Language.objects.exclude(id__in = LanguageManager.objects.filter(user_id = uid,
                                                                       status = 1).values('language'
                                                                                        )).values_list('id', 'name')
    for a_lang in lang_qs:
        data += '<option value = ' + str(a_lang[0]) + '>' \
            + str(a_lang[1]) + '</option>'
    return HttpResponse(json.dumps(data),
                        content_type = 'application/json')


def send_mail_to_contributor(contributor_id, tdid, lid, reason):
    tutorial_details = \
        TutorialResource.objects.filter(tutorial_detail_id = tdid,
                                        language = lid).values('tutorial_detail__tutorial',
                                                             'language__name', 'submissiondate')

    if reason:
        message_sub_date = '\n   - ' + 'Your submission date was : ' \
            + str(tutorial_details[0]['submissiondate']) \
            + ", but you could'nt complete before that."
    else:
    	message_sub_date = 'Quality standards not met.'

    user_details = \
        User.objects.filter(id = contributor_id).values('username',
                                                      'email')
    subject = 'Spoken Tutorials'
    message = 'Hello ' + str(user_details[0]['username']) + ''',

 ''' \
        + 'I am sorry to say that the tutorial,' \
        + tutorial_details[0]['tutorial_detail__tutorial'] \
        + ' has been removed from your tally for the following reasons : ' \
        + str(message_sub_date)
    email_list = [user_details[0]['email'], '']

    # check = send_mail(subject,message,'saurabh.adhikary@iitb.ac.in',
    # ('saurabh.adhikary@iitb.ac.in',),fail_silently = True)

    email = EmailMultiAlternatives(subject, message,
                                   'administrator@spoken-tutorial.org',
                                   to = email_list,
                                   headers = {'Content-type': 'text/html'
                                            })

    email.attach_alternative(message, 'text/html')
    result = email.send(fail_silently = False)
    return result

@login_required
def add_creation_notification(request, notif_type, user_id , language):
    notif_rec = None
    message = "You are now a "+str(language)
    title = ''

    try:
        if notif_type in (ROLES_DICT['contributor'],ROLES_DICT['external-contributor']):
            title = title + str(language) +" - Contributorship added"
            message = message+ " contributor"

            notif_rec = ContributorNotification.objects.create(user_id = user_id ,
                message = message , title = title)
        elif notif_type == ROLES_DICT['video-reviewer']:
            title = title +"Video Reviewership added"
            message = message+ " video reviewer"

            notif_rec = AdminReviewerNotification.objects.create(user_id = user_id ,
                message = "You are now a Video Reviewer" , title = title)
        elif notif_type == ROLES_DICT['domain-reviewer'] :
            title = title + str(language) +" - Domain Reviewership added"
            message = message+ " domain reviewer"
            notif_rec = DomainReviewerNotification.objects.create(user_id = user_id ,
                message = message , title = title)
        elif notif_type == ROLES_DICT['quality-reviewer'] :
            title = title + str(language) +" - Quality Reviewership added"
            message = message+ " quality reviewer"
            notif_rec = QualityReviewerNotification.objects.create(user_id = user_id ,
                message = message , title = title)
    except Exception as e:
        print("Notification already exists")
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@csrf_exempt
def update_tutorials(request):
    print("Reached here")
    action = request.POST['action']
    foss_name = request.POST['foss_name']
    data = ''

    #tutorials = TutorialDetail.objects.filter(foss__foss=foss_name)
    published_tutorials = TutorialResource.objects.filter(tutorial_detail__foss__foss=foss_name,
        status= PUBLISHED, language_id=22)
    all_langs = Language.objects.all().exclude(id=22)
    for tutorial in published_tutorials:
        print(tutorial.tutorial_detail.foss.foss,tutorial.tutorial_detail)
        for language in all_langs:
            this_tutorial_user_lang = TutorialResource.objects.filter(Q(
                    status=PUBLISHED)|Q(
                    assignment_status=ASSIGNMENT_STATUS_DICT['assigned']),
                    tutorial_detail=tutorial.tutorial_detail, language=language)
            tutorialsavailable=TutorialsAvailable.objects.filter(
                tutorial_detail=tutorial.tutorial_detail, language=language)
            if action == 'add':
                if not this_tutorial_user_lang.exists():
                    if not tutorialsavailable.exists():
                        new = TutorialsAvailable()
                        new.tutorial_detail = tutorial.tutorial_detail
                        new.language = language
                        new.save()
                        data = 'Updated'
            if action == 'remove':
                tutorialsavailable.delete()
                data = 'Removed'

    return HttpResponse(json.dumps(data),content_type='application/json')

@csrf_exempt
def grant_role(request):
    '''
    Grant all tutorials of the selected FOSS - only for english language
    '''
    action = request.POST['action']
    foss_id = request.POST['foss_id']
    user_id = request.POST['user_id']
    data = ''

    tuto_available = TutorialDetail.objects.filter(
            foss_id=foss_id).values_list('id','tutorial','level').order_by('level')

    for a_tutorial in tuto_available:
        contrib_roles = ContributorRole.objects.filter(user=user_id, tutorial_detail_id=a_tutorial[0], language_id=22)
        if action == 'add':
            if not contrib_roles.exists():
                new_con_role = ContributorRole()
                new_con_role.user_id = user_id
                new_con_role.foss_category_id = foss_id
                new_con_role.tutorial_detail_id = a_tutorial[0]
                new_con_role.language_id = 22
                new_con_role.status = 1
                new_con_role.save()
                data = "Role Added"
            else:
                data = "Role already exists"
        if action == 'remove':
            contrib_roles.update(status = 0, updated = timezone.now())
            data = "Role Deleted"
    return HttpResponse(json.dumps(data),content_type='application/json')
