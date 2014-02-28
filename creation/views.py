import os
import json
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views import generic
from django.views.decorators.http import require_POST
from jfu.http import upload_receive, UploadResponse, JFUResponse

from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django import forms

from creation.forms import *
from creation.models import *

def contributor_roles(request):
	form = ContributorRoleForm()
	context = {
		'form': form
	}
	context.update(csrf(request))
	return render_to_response('creation/templates/testingvis.html', context)

def testingvis(request):
	context = {
		'user': request.user
	}
	context.update(csrf(request))
	return render_to_response('creation/templates/testingvis.html', context)

def creationhome(request):
	context = {
		'user': request.user
	}
	context.update(csrf(request))
	return render_to_response('creation/templates/creationhome.html', context)

@login_required
def upload_tutorial_index(request):
	if request.method == 'POST':
		form = UploadTutorialForm(request.user, request.POST)
		if form.is_valid():
			common_content = Tutorial_Common_Content()
			if Tutorial_Common_Content.objects.filter(tutorial_detail_id = request.POST['tutorial_name']).count():
				common_content = Tutorial_Common_Content.objects.get(tutorial_detail_id = request.POST['tutorial_name'])
			else:
				tutorial_resource = Tutorial_Resource()
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
				tutorial_resource.tutorial_detail = common_content.tutorial_detail
				tutorial_resource.common_content = common_content
				tutorial_resource.language = Language.objects.get(pk = request.POST['language'])
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

			return HttpResponseRedirect('/creation/upload_tutorial/' + str(common_content.id) + '/' + str(tutorial_resource.id) + '/')
	else:
		form = UploadTutorialForm(user=request.user)

	context = {
		'form': form,
		'user': request.user
	}
	context.update(csrf(request))
	return render_to_response('creation/templates/upload_tutorial_index.html', context)

@csrf_exempt
def ajax_upload_foss(request):
	tmp = ''
	data = []
	if request.method == 'POST':
		foss = request.POST.get('foss')
		tutorials = Tutorial_Detail.objects.filter(foss_id = foss)
		for tutorial in tutorials:
			tmp += '<option value="' + str(tutorial.id) + '">' + tutorial.tutorial + '</option>'
		if(tmp):
			data.append('<option value=""></option>'+tmp)
		else:
			data.append(tmp)
		tmp = ''
		languages = Language.objects.filter(id__in=Contributor_Role.objects.filter(user_id=request.user.id, foss_category_id=foss).values_list('language_id'))
		for language in languages:
			tmp += '<option value="' + str(language.id) + '">' + language.name + '</option>'
		if(tmp):
			data.append('<option value=""></option>'+tmp)
		else:
			data.append(tmp)

	return HttpResponse(json.dumps(data), mimetype='application/json')

@login_required
def upload_tutorial(request, common_content_id, tutorial_resource_id):
	context = {
		'user': request.user,
		'trid': tutorial_resource_id
	}
	context.update(csrf(request))
	return render_to_response('creation/templates/upload_tutorial.html', context)

def upload_component(request, recid, component):
	if request.method == 'POST':
		form = ComponentForm(request.POST, request.FILES)
		if form.is_valid():
			file_path = settings.MEDIA_ROOT + request.FILES['comp'].name
			fout = open(file_path, 'wb+')
			f = request.FILES['comp']
			# Iterate through the chunks.
			for chunk in f.chunks():
				fout.write(chunk)
			fout.close()
			form = ComponentForm()
		
	else:
		form = ComponentForm()
	context = {
		'user': request.user,
		'form': form
	}
	context.update(csrf(request))
	return render_to_response('creation/templates/upload_component.html', context)
