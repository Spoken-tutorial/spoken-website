import os
import re
import json
import subprocess
from decimal import Decimal
from urllib2 import urlopen
from django.conf import settings
from django.views import generic
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST

from django import forms
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, render_to_response
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout

from creation.forms import *
from creation.models import *

def testingvis(request):
    context = {}
    context.update(csrf(request))
    return render(request, 'creation/templates/testingvis.html', context)

def is_contributor(user):
    """Check if the user is having contributor rights"""
    if user.groups.filter(name='Contributor').count() == 1:
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

def is_videoreviewer(user):
    """Check if the user is having video reviewer rights"""
    if user.groups.filter(name='Video-Reviewer').count() == 1:
        return True
    return False

def get_video_info(path):
    """Uses ffmpeg to determine information about a video."""
 
    process = subprocess.Popen(['/usr/bin/ffmpeg', '-i', path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    duration_m = re.search(r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?)", stdout, re.DOTALL).groupdict()
    info_m = re.search(r": Video: (?P<codec>.*?), (?P<profile>.*?), (?P<width>.*?)x(?P<height>.*?), (?P<fps>\d+?) fps, ", stdout, re.DOTALL).groupdict()

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
    info_m['height'] = int(info_m['height'])
    return info_m

def get_filesize(path):
    filesize_bytes = os.path.getsize(path)

def creationhome(request):
    context = {}
    context.update(csrf(request))
    return render(request, 'creation/templates/creationhome.html', context)

@login_required
def upload_tutorial_index(request):
    if not is_contributor(request.user):
        raise PermissionDenied()
    if request.method == 'POST':
        form = UploadTutorialForm(request.user, request.POST)
        lang = None
        if form.is_valid():
            lang = Language.objects.get(pk = int(request.POST['language']))
            common_content = Tutorial_Common_Content()
            if Tutorial_Common_Content.objects.filter(tutorial_detail_id = request.POST['tutorial_name']).count():
                common_content = Tutorial_Common_Content.objects.get(tutorial_detail_id = request.POST['tutorial_name'])
            else:
                common_content.tutorial_detail = Tutorial_Detail.objects.get(pk = request.POST['tutorial_name'])
                common_content.slide_user = request.user
                common_content.slide_status = 0
                common_content.code_user = request.user
                common_content.code_status = 0
                common_content.assignment_user = request.user
                common_content.assignment_status = 0
                common_content.prerequisit_user = request.user
                common_content.prerequisit_status = 0
                common_content.keyword_user = request.user
                common_content.keyword_status = 0
                common_content.save()
            if Tutorial_Resource.objects.filter(tutorial_detail_id = request.POST['tutorial_name'], common_content_id = common_content.id, language_id = request.POST['language']).count():
                tutorial_resource = Tutorial_Resource.objects.get(tutorial_detail_id = request.POST['tutorial_name'], common_content_id = common_content.id, language_id = request.POST['language'])
            else:
                tutorial_resource = Tutorial_Resource()
                tutorial_resource.tutorial_detail = common_content.tutorial_detail
                tutorial_resource.common_content = common_content
                tutorial_resource.language = lang
                tutorial_resource.outline_user = request.user
                tutorial_resource.outline_status = 0
                tutorial_resource.script_user = request.user
                tutorial_resource.script_status = 0
                tutorial_resource.video_user = request.user
                tutorial_resource.video_status = 0
                tutorial_resource.status = 0
                tutorial_resource.version = 0
                tutorial_resource.hit_count = 0
                tutorial_resource.save()

            return HttpResponseRedirect('/creation/upload-tutorial/' + str(tutorial_resource.id) + '/')
    else:
        form = UploadTutorialForm(user=request.user)

    context = {
        'form': form,
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_tutorial_index.html', context)

@login_required
@csrf_exempt
def ajax_upload_foss(request):
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
            lang_rec = Language.objects.get(pk = int(lang))
            if lang_rec.name == 'English':
                td_list = Tutorial_Detail.objects.filter(foss_id = foss).values_list('id')
                tutorials = Tutorial_Detail.objects.filter(
                    id__in = td_list
                ).exclude(
                    id__in = Tutorial_Resource.objects.filter(
                        tutorial_detail_id__in = td_list,
                        language_id = lang_rec.id,
                        status = 1
                        ).values_list(
                            'tutorial_detail_id'
                        )
                )
            else:
                lang_rec = Language.objects.get(name = 'English')
                td_list = Tutorial_Detail.objects.filter(foss_id = foss).values_list('id')
                tutorials = Tutorial_Detail.objects.filter(
                    id__in = Tutorial_Resource.objects.filter(
                        tutorial_detail_id__in = td_list,
                        language_id = lang_rec.id,
                        status = 1
                    ).values_list(
                        'tutorial_detail_id'
                    )
                )
            for tutorial in tutorials:
                data += '<option value="' + str(tutorial.id) + '">' + tutorial.tutorial + '</option>'
            if data:
                data = '<option value=""></option>' + data
        elif foss:
            languages = Language.objects.filter(id__in=Contributor_Role.objects.filter(user_id=request.user.id, foss_category_id=foss).values_list('language_id'))
            for language in languages:
                data += '<option value="' + str(language.id) + '">' + language.name + '</option>'
            if data:
                data = '<option value=""></option>' + data

    return HttpResponse(json.dumps(data), mimetype='application/json')

@login_required
def upload_tutorial(request, trid):
    tr_rec = None
    contrib_log = None
    review_log = None
    try:
        tr_rec = Tutorial_Resource.objects.get(pk = trid)
        Contributor_Role.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
        contrib_log = Contributor_Log.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_log = Need_Improvement_Log.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
    except Exception, e:
        print e
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
def upload_component(request, trid, component):
    tr_rec = None
    comp_log = Contributor_Log()
    try:
        tr_rec = Tutorial_Resource.objects.get(pk = trid)
        Contributor_Role.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        print e
        raise PermissionDenied()
    if request.method == 'POST':
        response_msg = ''
        error_msg = ''
        form = ComponentForm(component, request.POST, request.FILES)
        if form.is_valid():
            try:
                comp_log.user = request.user
                comp_log.tutorial_resource = tr_rec
                comp_log.component = component
                if component == 'video':
                    file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                    file_name =  tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-' + tr_rec.language.name + file_extension
                    file_path = settings.MEDIA_ROOT + 'videos/' + str(tr_rec.tutorial_detail.foss_id) + '/' + str(tr_rec.tutorial_detail.id) + '/' + file_name
                    fout = open(file_path, 'wb+')
                    f = request.FILES['comp']
                    # Iterate through the chunks.
                    for chunk in f.chunks():
                        fout.write(chunk)
                    fout.close()
                    comp_log.status = tr_rec.video_status
                    tr_rec.video = file_name
                    tr_rec.video_user = request.user
                    tr_rec.video_status = 1
                    tr_rec.save()
                    comp_log.save()
                    response_msg = 'Video uploaded successfully!'
                elif component == 'slide':
                    file_name, file_extension = os.path.splitext(request.FILES['comp'].name)
                    file_name =  tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '-Slides' + file_extension
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
                    response_msg = 'Assignment file uploaded successfully!'
                #return HttpResponse(response_msg)
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
                'title': component,
            }
            context.update(csrf(request))
            return render(request, 'creation/templates/upload_component.html', context)
        else:
            tutorial_resource = Tutorial_Resource.objects.get(pk = trid)
            context = {
                'form': form,
                'title': component,
            }
            context.update(csrf(request))
            return render(request, 'creation/templates/upload_component.html', context)
        
    form = ComponentForm(component)
    tutorial_resource = Tutorial_Resource.objects.get(pk = trid)
    context = {
        'form': form,
        'title': component,
        'tutorial_resource': tutorial_resource
    }
    context.update(csrf(request))
    return render(request, 'creation/templates/upload_component.html', context)

def upload_outline(request, trid):
    tr_rec = None
    comp_log = Contributor_Log()
    try:
        tr_rec = Tutorial_Resource.objects.get(pk = trid)
        Contributor_Role.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        print e
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    warning_msg = ''
    if request.method == 'POST':
        form = UploadOutlineForm(trid, request.POST)
        if form.is_valid():
            try:
                comp_log.status = tr_rec.outline_status
                if tr_rec.outline != request.POST['outline']:
                    tr_rec.outline = request.POST['outline']
                    tr_rec.outline_user = request.user
                    tr_rec.outline_status = 2
                    tr_rec.save()
                    comp_log.user = request.user
                    comp_log.tutorial_resource = tr_rec
                    comp_log.component = 'outline'
                    comp_log.save()
                    response_msg = 'Outline uploaded successfully!'
                else:
                    warning_msg = 'There is no change in outline'
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

def upload_script(request, trid):
    tr_rec = None
    comp_log = Contributor_Log()
    try:
        tr_rec = Tutorial_Resource.objects.get(pk = trid)
        Contributor_Role.objects.get(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1)
    except Exception, e:
        print e
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    storage_path = tr_rec.tutorial_detail.foss.foss + '/' + tr_rec.tutorial_detail.level.code + '/' + tr_rec.tutorial_detail.tutorial.replace(' ', '-') + '/' + tr_rec.language.name
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
                    print type(code)
                if(int(code) == 200):
                    comp_log.status = tr_rec.script_status
                    tr_rec.script = storage_path
                    tr_rec.script_user = request.user
                    tr_rec.script_status = 2
                    tr_rec.save()
                    comp_log.user = request.user
                    comp_log.tutorial_resource = tr_rec
                    comp_log.component = 'script'
                    comp_log.save()
                    response_msg = 'Script uploaded successfully'
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

def mark_notrequired(request, tcid, component):
    tcc = None
    try:
        tcc = Tutorial_Common_Content.objects.get(pk = tcid)
        if getattr(tcc, component + '_status') != 4:
            if component == 'code':
                tcc.code_status = 6
            elif component == 'assignment':
                tcc.assignment_status = 6
            tcc.save()
            messages.success(request, component + " status updated successfully!")
        else:
            messages.error(request, "Invalid resource id!")
    except Exception, e:
        messages.error(request, 'Something went wrong, please try after some time.')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def view_outline(request, trid):
    tr_rec = None
    try:
        tr_rec = Tutorial_Resource.objects.get(pk = trid)
    except Exception, e:
        print e
        raise PermissionDenied()
    if tr_rec.outline:
        context = {
            'tr': tr_rec,
        }
        context.update(csrf(request))
        return render(request, 'creation/templates/view_outline.html', context)
    else:
        raise PermissionDenied()

def view_video(request, trid):
    tr = None
    try:
        tr = Tutorial_Resource.objects.get(pk = trid)
    except Exception, e:
        print e
        raise PermissionDenied()
    if tr.video:
        video_path = settings.MEDIA_ROOT + "videos/" + str(tr.tutorial_detail.foss_id) + "/" + str(tr.tutorial_detail_id) + "/" + tr.video
        video_info = get_video_info(video_path)
        context = {
            'tr': tr,
            'video_info': video_info,
            'media_url': settings.MEDIA_URL
        }
        context.update(csrf(request))
        return render(request, 'creation/templates/view_video.html', context)
    else:
        raise PermissionDenied()

def tutorials_contributed(request):
    if is_contributor(request.user):
        contrib_list = ''
        context = {
            'tr_objs': '',
            'media_url': settings.MEDIA_URL
        }
        return render(request, 'creation/templates/my_contribs.html', context)
    else:
        raise PermissionDenied()

def admin_review_index(request):
    if not is_videoreviewer(request.user):
        raise PermissionDenied()
    tr_recs = None
    try:
        tr_recs = Tutorial_Resource.objects.filter(video_status = 1).order_by('updated')
        context = {
            'tr_recs': tr_recs
        }
        return render(request, 'creation/templates/admin_review_index.html', context)
    except Exception, e:
        return e

def review_video(request, trid):
    if not is_videoreviewer(request.user):
        raise PermissionDenied()
    try:
        tr = Tutorial_Resource.objects.get(pk = trid)
    except:
        raise PermissionDenied()
    response_msg = ''
    error_msg = ''
    if request.method == 'POST':
        form = ReviewVideoForm(request.POST)
        if form.is_valid():
            print request.POST['video_status']
            form = ReviewVideoForm()
            if request.POST['video_status'] == '2':
                try:
                    tr.video_status = 2
                    tr.save()
                    vr_log = Video_Review_Log()
                    vr_log.status = tr.video_status
                    vr_log.user = request.user
                    vr_log.tutorial_resource = tr
                    vr_log.save()
                    response_msg = 'Review status updated successfully!'
                except:
                    error_msg = 'Something went wrong, please try again later.'
            elif request.POST['video_status'] == '5':
                try:
                    prev_state = tr.video_status
                    tr.video_status = 5
                    tr.save()
                    ni_log = Need_Improvement_Log()
                    ni_log.user = request.user
                    ni_log.tutorial_resource = tr
                    ni_log.review_state = prev_state
                    ni_log.component = 'video'
                    ni_log.comment = request.POST['feedback']
                    ni_log.flag = 1
                    ni_log.save()
                    vr_log = Video_Review_Log()
                    vr_log.status = tr.video_status
                    vr_log.user = request.user
                    vr_log.tutorial_resource = tr
                    vr_log.save()
                    response_msg = 'Review status updated successfully!'
                except:
                    error_msg = 'Something went wrong, please try again later.'
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
    return render(request, 'creation/templates/review_video.html', context)

def domain_review_index(request):
    if not is_domainreviewer(request.user):
        raise PermissionDenied()
    tmp_recs = []
    dr_roles =  Domain_Reviewer_Role.objects.filter(user_id = request.user.id, status = 1)
    for rec in dr_roles:
        tr_recs = Tutorial_Resource.objects.select_related().filter(tutorial_detail_id__in = Tutorial_Detail.objects.filter(foss_id = rec.foss_category_id).values_list('id'), language_id = rec.language_id, status = 0).order_by('updated')
        for tr_rec in tr_recs:
            tmp_recs.append(tr_rec)
    context = {
        'tr_recs': sorted(tmp_recs, key=lambda tutorial_resource: tutorial_resource.updated)
    }
    return render(request, 'creation/templates/domain_review_index.html', context)

def domain_review_tutorial(request, trid):
    if not is_domainreviewer(request.user):
        raise PermissionDenied()
    tr_rec = Tutorial_Resource.objects.select_related().get(pk = trid)
    if Domain_Reviewer_Role.objects.filter(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1).count() == 0:
        raise PermissionDenied()
    try:
        contrib_log = Contributor_Log.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_log = Need_Improvement_Log.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_history = Domain_Review_Log.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
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

def domain_review_component(request, trid, component):
    if not is_domainreviewer(request.user):
        raise PermissionDenied()
    tr = Tutorial_Resource.objects.select_related().get(pk = trid)
    if Domain_Reviewer_Role.objects.filter(user_id = request.user.id, foss_category_id = tr.tutorial_detail.foss_id, language_id = tr.language_id).count() == 0:
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
                        dr_log = Domain_Review_Log()
                        dr_log.status = 3
                        dr_log.component = component
                        dr_log.user = request.user
                        dr_log.tutorial_resource = tr
                        dr_log.save()
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
                    ni_log = Need_Improvement_Log()
                    ni_log.user = request.user
                    ni_log.tutorial_resource = tr
                    ni_log.review_state = prev_state
                    ni_log.component = component
                    ni_log.comment = request.POST['feedback']
                    ni_log.flag = 1
                    ni_log.save()
                    dr_log = Domain_Review_Log()
                    dr_log.status = 5
                    dr_log.component = component
                    dr_log.user = request.user
                    dr_log.tutorial_resource = tr
                    dr_log.save()
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

def quality_review_index(request):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tmp_recs = []
    com_recs = []
    qr_roles =  Quality_Reviewer_Role.objects.filter(user_id = request.user.id, status = 1)
    for rec in qr_roles:
        tr_recs = Tutorial_Resource.objects.select_related().filter(tutorial_detail_id__in = Tutorial_Detail.objects.filter(foss_id = rec.foss_category_id).values_list('id'), language_id = rec.language_id, status = 0).order_by('updated')
        for tr_rec in tr_recs:
            if tr_rec.outline_status == 3 or tr_rec.script_status == 3 or tr_rec.video_status == 3:
                tmp_recs.append(tr_rec)
            elif tr_rec.language.name == 'English' and tr_rec.common_content.slide_status == 3 or tr_rec.common_content.code_status == 3 or tr_rec.common_content.assignment_status == 3:
                tmp_recs.append(tr_rec)
            else:
                flag = 0
                if tr_rec.language.name == 'English':
                    if tr_rec.common_content.slide_status == 4 and (tr_rec.common_content.code_status == 4 or tr_rec.common_content.code_status == 6) and (tr_rec.common_content.assignment_status == 4 or tr_rec.common_content.assignment_status == 6):
                        flag = 1
                else:
                    flag = 1
                if flag and tr_rec.outline_status == 4 or tr_rec.script_status == 4 or tr_rec.video_status == 4:
                    com_recs.append(tr_rec)
    context = {
        'tr_recs': sorted(tmp_recs, key=lambda tutorial_resource: tutorial_resource.updated),
        'com_recs': sorted(com_recs, key=lambda tutorial_resource: tutorial_resource.updated)
    }
    return render(request, 'creation/templates/quality_review_index.html', context)

def quality_review_tutorial(request, trid):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tr_rec = Tutorial_Resource.objects.select_related().get(pk = trid)
    if Quality_Reviewer_Role.objects.filter(user_id = request.user.id, foss_category_id = tr_rec.tutorial_detail.foss_id, language_id = tr_rec.language_id, status = 1).count() == 0:
        raise PermissionDenied()
    try:
        contrib_log = Contributor_Log.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_log = Need_Improvement_Log.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
        review_history = Quality_Review_Log.objects.filter(tutorial_resource_id = tr_rec.id).order_by('-created')
    except:
        contrib_log = None
        review_log = None
        review_history = None
    context = {
        'tr': tr_rec,
        'contrib_log': contrib_log,
        'review_log': review_log,
        'review_history': review_history
    }
    return render(request, 'creation/templates/quality_review_tutorial.html', context)

def quality_review_component(request, trid, component):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tr = Tutorial_Resource.objects.select_related().get(pk = trid)
    if Quality_Reviewer_Role.objects.filter(user_id = request.user.id, foss_category_id = tr.tutorial_detail.foss_id, language_id = tr.language_id).count() == 0:
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
                        dr_log = Quality_Review_Log()
                        dr_log.status = 4
                        dr_log.component = component
                        dr_log.user = request.user
                        dr_log.tutorial_resource = tr
                        dr_log.save()
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
                    ni_log = Need_Improvement_Log()
                    ni_log.user = request.user
                    ni_log.tutorial_resource = tr
                    ni_log.review_state = prev_state
                    ni_log.component = component
                    ni_log.comment = request.POST['feedback']
                    ni_log.flag = 1
                    ni_log.save()
                    dr_log = Quality_Review_Log()
                    dr_log.status = 5
                    dr_log.component = component
                    dr_log.user = request.user
                    dr_log.tutorial_resource = tr
                    dr_log.save()
                    response_msg = 'Review status updated successfully!'
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
    }

    return render(request, 'creation/templates/quality_review_component.html', context)

def accept_all(request, review, trid):
    status_flag = {
        'domain': 3,
        'quality': 4
    }
    if not is_domainreviewer(request.user):
        raise PermissionDenied()
    tr = Tutorial_Resource.objects.select_related().get(pk = trid)
    if Domain_Reviewer_Role.objects.filter(user_id = request.user.id, foss_category_id = tr.tutorial_detail.foss_id, language_id = tr.language_id).count() == 0:
        raise PermissionDenied()
    current_status = status_flag[review] - 1
    if tr.outline_status > 0 and tr.outline_status == current_status:
        tr.outline_status = status_flag[review]
        if review == 'quality':
            dr_log = Quality_Review_Log()
        else:
            dr_log = Domain_Review_Log()
        dr_log.status = status_flag[review]
        dr_log.component = "outline"
        dr_log.user = request.user
        dr_log.tutorial_resource = tr
        dr_log.save()
    if tr.script_status > 0 and tr.script_status == current_status:
        tr.script_status = status_flag[review]
        if review == 'quality':
            dr_log = Quality_Review_Log()
        else:
            dr_log = Domain_Review_Log()
        dr_log.status = status_flag[review]
        dr_log.component = "script"
        dr_log.user = request.user
        dr_log.tutorial_resource = tr
        dr_log.save()
    if tr.video_status > 0 and tr.video_status == current_status:
        tr.video_status = status_flag[review]
        if review == 'quality':
            dr_log = Quality_Review_Log()
        else:
            dr_log = Domain_Review_Log()
        dr_log.status = status_flag[review]
        dr_log.component = "video"
        dr_log.user = request.user
        dr_log.tutorial_resource = tr
        dr_log.save()
    tr.save()
    if tr.language.name == 'English':
        if tr.common_content.slide_status > 0 and tr.common_content.slide_status == current_status:
            tr.common_content.slide_status = status_flag[review]
            if review == 'quality':
                dr_log = Quality_Review_Log()
            else:
                dr_log = Domain_Review_Log()
            dr_log.status = status_flag[review]
            dr_log.component = "slide"
            dr_log.user = request.user
            dr_log.tutorial_resource = tr
            dr_log.save()
        if tr.common_content.code_status > 0 and tr.common_content.code_status == current_status:
            tr.common_content.code_status = status_flag[review]
            if review == 'quality':
                dr_log = Quality_Review_Log()
            else:
                dr_log = Domain_Review_Log()
            dr_log.status = status_flag[review]
            dr_log.component = "code"
            dr_log.user = request.user
            dr_log.tutorial_resource = tr
            dr_log.save()
        if tr.common_content.assignment_status > 0 and tr.common_content.assignment_status == current_status:
            tr.common_content.assignment_status = status_flag[review]
            if review == 'quality':
                dr_log = Quality_Review_Log()
            else:
                dr_log = Domain_Review_Log()
            dr_log.status = status_flag[review]
            dr_log.component = "assignment"
            dr_log.user = request.user
            dr_log.tutorial_resource = tr
            dr_log.save()
    tr.common_content.save()

    return HttpResponseRedirect('/creation/' + review + '-review-tutorial/' + str(tr.id) + '/')

def publish_tutorial(request, trid):
    if not is_qualityreviewer(request.user):
        raise PermissionDenied()
    tr = Tutorial_Resource.objects.select_related().get(pk = trid)
    if Quality_Reviewer_Role.objects.filter(user_id = request.user.id, foss_category_id = tr.tutorial_detail.foss_id, language_id = tr.language_id).count() == 0:
        raise PermissionDenied()
    flag = 0
    if tr.language.name == 'English':
        if tr.common_content.slide_status == 4 and (tr.common_content.code_status == 4 or tr.common_content.code_status == 6) and (tr.common_content.assignment_status == 4 or tr.common_content.assignment_status == 6):
            flag = 1
    else:
        flag = 1
    if flag and tr.outline_status == 4 or tr.script_status == 4 or tr.video_status == 4:
        if tr.status == 0:
            tr.status = 1
            tr.save()
            messages.success(request, 'Tutorial published successfully!')
        else:
            messages.warning(request, 'Tutorial already published')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
