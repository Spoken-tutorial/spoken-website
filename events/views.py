from django.core.context_processors import csrf
from django.core.exceptions import PermissionDenied

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages

from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

from django.views.decorators.csrf import csrf_exempt

from django.http import Http404
from django.db.models import Q

from urlparse import urlparse

from BeautifulSoup import BeautifulSoup

import xml.etree.cElementTree as etree

import json
import urllib,urllib2

from events.models import *
from cms.models import Profile

from forms import *

def is_event_manager(user):
	"""Check if the user is having event manger  rights"""
	if user.groups.filter(name='Event Manager').count() == 1:
		return True
		
def is_resource_person(user):
	"""Check if the user is having resource person  rights"""
	if user.groups.filter(name='Resource Person').count() == 1:
		return True
		
def is_organiser(user):
	"""Check if the user is having organiser rights"""
	try:
		if user.groups.filter(name='Organiser').count() == 1 and user.organiser and user.organiser.status == 1:
			return True
	except:
		pass

def is_invigilator(user):
	"""Check if the user is having invigilator rights"""
	if user.groups.filter(name='Invigilator').count() == 1:
		return True

@login_required
def new_ac(request):
	""" Create new academic center. Academic code generate by autimatic.
		if any code missing in between first assign that code then continue the serial
	"""
	user = request.user
	if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
		
	if request.method == 'POST':
		form = AcademicForm(user, request.POST)
		if form.is_valid():
			form_data = form.save(commit=False)
			form_data.user_id = user.id
			
			state = form.cleaned_data['state']
			# find the academic code available number
			try:
				ac = AcademicCenter.objects.filter(state = state).order_by('-academic_code')[:1].get()
			except:
				#print "This is first record!!!"
				ac = None
				academic_code = 1
				
			if ac:
				code_range = int(ac.academic_code.split('-')[1])
				available_code_range = []
				for i in range(code_range):
					available_code_range.insert(i, i+1)
				
				#find the existing numbers
				ac = AcademicCenter.objects.filter(state = state).order_by('-academic_code')
				for record in ac:
					a = int(record.academic_code.split('-')[1])-1
					available_code_range[a] = 0
				
				academic_code = code_range + 1
				#finding Missing number
				for code in available_code_range:
					if code != 0:
						academic_code = code
						break

			# Generate academic code
			if academic_code < 10:
				ac_code = '0000'+str(academic_code)
			elif academic_code <= 99:
				ac_code = '000'+str(academic_code)
			elif academic_code <= 999:
				ac_code = '00'+str(academic_code)
			elif academic_code <= 9999:
				ac_code = '0'+str(academic_code)
			
			#get state code
			state_code = State.objects.get(pk = state.id).code
			academic_code = state_code +'-'+ ac_code
			
			form_data.academic_code = academic_code
			form_data.save()
			return HttpResponseRedirect("/events/ac/")
		
		context = {'form':form}
		return render(request, 'events/templates/ac/form.html', context)
	else:
		context = {}
		context.update(csrf(request))
		context['form'] = AcademicForm(user=request.user)
		return render(request, 'events/templates/ac/form.html', context)

@login_required
def edit_ac(request, rid = None):
	""" Edit academic center """
	user = request.user
	if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
		
	if request.method == 'POST':
		contact = AcademicCenter.objects.get(id = rid)
		form = AcademicForm(request.user, request.POST, instance=contact)
		if form.is_valid():
			if form.save():
				return HttpResponseRedirect("/events/ac/")
		context = {'form':form}
		return render(request, 'events/templates/ac/form.html', context)
	else:
		try:
			record = AcademicCenter.objects.get(id = rid)
			context = {}
			context['form'] = AcademicForm(user=request.user, instance = record)
			context['edit'] = rid
			context.update(csrf(request))
			return render(request, 'events/templates/ac/form.html', context)
		except:
			raise Http404('Page not found')

@login_required
def ac(request):
	""" Academic index page """
	user = request.user
	if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
		
	context = {}
	context['collection'] = AcademicCenter.objects.all
	context['model'] = "Academic Center"
	context.update(csrf(request))
	return render(request, 'events/templates/ac/index.html', context)
	return HttpResponse('RP!')

def has_profile_data(request, user):
	''' check weather user profile having blank data or not '''
	if user:
		profile = Profile.objects.filter(user=user).first()
		if not profile:
			return HttpResponseRedirect("/accounts/profile/"+user.username+"/")
	
		for field in profile._meta.get_all_field_names():
			if not getattr(profile, field, None):
				return HttpResponseRedirect("/accounts/profile/"+user.username+"/")

@login_required
def organiser_request(request, username):
	""" request to bacome a new organiser """
	user = request.user
	if not user.is_authenticated():
		raise Http404('You are not allowed to view this page!')
		
	if username == request.user.username:
		user = User.objects.get(username=username)
		if request.method == 'POST':
			form = OrganiserForm(request.POST)
			if form.is_valid():
				user.groups.add(Group.objects.get(name='Organiser'))
				organiser = Organiser()
				organiser.user_id=request.user.id
				organiser.academic_id=request.POST['college']
				organiser.save()
				return HttpResponseRedirect("/events/organiser/view/"+user.username+"/")
			context = {'form':form}
			return render(request, 'events/templates/organiser/form.html', context)
		else:
			try:
				organiser = Organiser.objects.get(user=user)
				#todo: send status message
				if organiser.status:
					print "you have already organiser role !!"
					return HttpResponseRedirect("/events/organiser/view/"+user.username+"/")
				else:
					print "Organiser not yet approve !!"
					return HttpResponseRedirect("/events/organiser/view/"+user.username+"/")
			except:
				context = {}
				context.update(csrf(request))
				context['form'] = OrganiserForm()
				return render(request, 'events/templates/organiser/form.html', context)
	else:
		raise Http404('You are not allowed to view this page!')

@login_required
def organiser_view(request, username):
	""" view organiser details """
	user = request.user
	if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
	
	user = User.objects.get(username=username)
	context = {}
	organiser = Organiser.objects.get(user=user)
	context['record'] = organiser
	try:
		profile = organiser.user.profile_set.get()
	except:
		profile = ''
	context['profile'] = profile
	return render(request, 'events/templates/organiser/view.html', context)

#@login_required
def organiser_edit(request, username):
	""" view organiser details """
	#todo: confirm event_manager and resource_center can edit organiser details
	user = request.user
	if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
		
	user = User.objects.get(username=username)
	if request.method == 'POST':
		form = OrganiserForm(request.POST)
		if form.is_valid():
			organiser = Organiser.objects.get(user=user)
			#organiser.user_id=request.user.id
			organiser.academic_id=request.POST['college']
			organiser.save()
			return HttpResponseRedirect("/events/organiser/view/"+user.username+"/")
		context = {'form':form}
		return render(request, 'events/templates/organiser/form.html', context)
	else:
			#todo : if any workshop and test under this organiser disable the edit
			record = Organiser.objects.get(user=user)
			context = {}
			context['form'] = OrganiserForm(instance = record)
			context.update(csrf(request))
			return render(request, 'events/templates/organiser/form.html', context)

@login_required
def rp_organiser(request, status = None):
	""" Resource person: List all inactive organiser under resource person states """
	#todo: filter to diaplay block and active user
	user = request.user
	if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
	if status == 'active':
		status = 1
	elif status == 'inactive':
		status = 0
	elif status == 'blocked':
		status = 2
	else:
		raise Http404('Page not found !!')
		
	user = User.objects.get(pk=user.id)
	try:
		organiser = Organiser.objects.filter(academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)), status=status)
	except:
		organiser = {}
	context = {}
	context['collection'] = organiser
	context['active'] = status
	return render(request, 'events/templates/rp/organiser.html', context)

@login_required
def rp_organiser_confirm(request, code, userid):
	""" Resource person: active organiser """
	user = request.user
	organiser_in_rp_state = Organiser.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
	if not (user.is_authenticated() and organiser_in_rp_state and ( is_event_manager(user) or is_resource_person(user))):
		raise PermissionDenied('You are not allowed to view this page!')

	try:
		if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
			organiser = Organiser.objects.get(user_id = userid)
			organiser.appoved_by_id = request.user.id
			organiser.status = 1
			organiser.save()
			return HttpResponseRedirect('/events/organiser/active/')
		else:
			raise Http404('Page not found !!')
	except:
		raise PermissionDenied('You are not allowed to view this page!')

@login_required
def rp_organiser_block(request, code, userid):
	""" Resource person: block organiser """
	#todo: if user block, again he trying to register, display message your accout blocked by rp contact rp
	user = request.user
	organiser_in_rp_state = Organiser.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
	if not (user.is_authenticated() and organiser_in_rp_state and ( is_event_manager(user) or is_resource_person(user))):
		raise PermissionDenied('You are not allowed to view this page!')

	try:
		if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
			organiser = Organiser.objects.get(user_id = userid)
			organiser.appoved_by_id = request.user.id
			organiser.status = 2
			organiser.save()
			return HttpResponseRedirect('/events/organiser/active/')
		else:
			raise Http404('Page not found !!')
	except:
		raise PermissionDenied('You are not allowed to view this page!')

@login_required
def invigilator_request(request, username):
	""" Request to bacome a invigilator """
	user = request.user
	if not user.is_authenticated():
		raise Http404('You are not allowed to view this page!')

	if username == user.username:
		user = User.objects.get(username=username)
		if request.method == 'POST':
			form = InvigilatorForm(request.POST)
			if form.is_valid():
				user.groups.add(Group.objects.get(name='invigilator'))
				invigilator = Invigilator()
				invigilator.user_id=request.user.id
				invigilator.academic_id=request.POST['college']
				invigilator.save()
				return HttpResponseRedirect("/events/invigilator/view/"+user.username+"/")
			context = {'form':form}
			return render(request, 'events/templates/invigilator/form.html', context)
		else:
			try:
				invigilator = Invigilator.objects.get(user=user)
				#todo: send status message
				if invigilator.status:
					print "you have already invigilator role !!"
					return HttpResponseRedirect("/events/invigilator/view/"+user.username+"/")
				else:
					print "invigilator not yet approve !!"
					return HttpResponseRedirect("/events/invigilator/view/"+user.username+"/")
			except:
				context = {}
				context.update(csrf(request))
				context['form'] = InvigilatorForm()
				return render(request, 'events/templates/invigilator/form.html', context)
	else:
		raise Http404('You are not allowed to view this page!')

@login_required
def invigilator_view(request, username):
	""" Invigilator view page """
	user = request.user
	if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
	
	user = User.objects.get(username=username)
	context = {}
	invigilator = Invigilator.objects.get(user=user)
	context['record'] = invigilator
	try:
		profile = invigilator.user.profile_set.get()
	except:
		profile = ''
	context['profile'] = profile
	return render(request, 'events/templates/invigilator/view.html', context)
	
@login_required
def invigilator_edit(request, username):
	""" Invigilator edit page """
	user = request.user
	if not (user.is_authenticated() and (username == request.user.username or is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
		
	user = User.objects.get(username=username)
	if request.method == 'POST':
		form = InvigilatorForm(request.POST)
		if form.is_valid():
			invigilator = Invigilator.objects.get(user=user)
			invigilator.academic_id=request.POST['college']
			invigilator.save()
			return HttpResponseRedirect("/events/invigilator/view/"+user.username+"/")
		context = {'form':form}
		return render(request, 'events/templates/invigilator/form.html', context)
	else:
			#todo : if any workshop and test under this invigilator disable the edit
			record = Invigilator.objects.get(user=user)
			context = {}
			context['form'] = InvigilatorForm(instance = record)
			context.update(csrf(request))
			return render(request, 'events/templates/invigilator/form.html', context)

@login_required
def rp_invigilator(request, status = None):
	print "ssssss", status
	""" Resource person: List all inactive Invigilator under resource person states """
	#todo: filter to diaplay block and active user
	user = request.user
	if not (user.is_authenticated() and (is_event_manager(user) or is_resource_person(user))):
		raise Http404('You are not allowed to view this page!')
	if status == 'active':
		status = 1
	elif status == 'inactive':
		status = 0
	elif status == 'blocked':
		status = 2
	else:
		raise Http404('Page not found !!')
		
	user = User.objects.get(pk=user.id)
	try:
		invigilator = Invigilator.objects.filter(academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)), status=status)
	except:
		invigilator = {}
	context = {}
	context['collection'] = invigilator
	context['active'] = status
	return render(request, 'events/templates/rp/invigilator.html', context)

@login_required
def rp_invigilator_confirm(request, code, userid):
	""" Resource person: active invigilator """
	user = request.user
	invigilator_in_rp_state = Invigilator.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
	if not (user.is_authenticated() and invigilator_in_rp_state and ( is_event_manager(user) or is_resource_person(user))):
		raise PermissionDenied('You are not allowed to view this page!')

	try:
		if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
			invigilator = Invigilator.objects.get(user_id = userid)
			invigilator.appoved_by_id = request.user.id
			invigilator.status = 1
			invigilator.save()
			return HttpResponseRedirect('/events/invigilator/active/')
		else:
			raise Http404('Page not found !!')
	except:
		raise PermissionDenied('You are not allowed to view this page!')

@login_required
def rp_invigilator_block(request, code, userid):
	""" Resource person: block invigilator """
	#todo: if user block, again he trying to register, display message your accout blocked by rp contact rp
	user = request.user
	invigilator_in_rp_state = Invigilator.objects.filter(user_id=userid, academic=AcademicCenter.objects.filter(state=State.objects.filter(resourceperson__user_id=user)))
	if not (user.is_authenticated() and invigilator_in_rp_state and ( is_event_manager(user) or is_resource_person(user))):
		raise PermissionDenied('You are not allowed to view this page!')

	try:
		if User.objects.get(pk=userid).profile_set.get().confirmation_code == code:
			invigilator = Invigilator.objects.get(user_id = userid)
			invigilator.appoved_by_id = request.user.id
			invigilator.status = 2
			invigilator.save()
			return HttpResponseRedirect('/events/invigilator/active/')
		else:
			raise Http404('Page not found !!')
	except:
		raise PermissionDenied('You are not allowed to view this page!')

@login_required
def workshop_request(request):
	''' Workshop request by organiser '''
	user = request.user
	if not user.is_authenticated() or not is_organiser(user):
		raise Http404('You are not allowed to view this page!')
	
	if request.method == 'POST':
		form = WorkshopForm(request.POST, user = request.user)
		if form.is_valid():
			dateTime = request.POST['wdate'].split(' ')
			w = Workshop()
			w.organiser_id = user.id
			w.academic_id = request.POST['academic']
			w.language_id = request.POST['language']
			w.foss_id = request.POST['foss']
			w.wdate = dateTime[0]
			w.wtime = dateTime[1]
			w.skype = request.POST['skype']
			w.save()
			#M2M saving department
			for dept in form.cleaned_data.get('department'):
				w.department.add(dept)
			w.save()
			return HttpResponseRedirect("/events/workshop/pending/")
		
		context = {'form':form, }
		return render(request, 'events/templates/workshop/form.html', context)
	else:
		context = {}
		context.update(csrf(request))
		context['form'] = WorkshopForm(user = request.user)
		return render(request, 'events/templates/workshop/form.html', context)

def workshop_edit(request, rid):
	''' Workshop edit by organiser or resource person '''
	user = request.user
	if not user.is_authenticated() or not is_organiser:
		raise Http404('You are not allowed to view this page!')
	
	if request.method == 'POST':
		form = WorkshopForm(request.POST, user = request.user)
		if form.is_valid():
			print form.cleaned_data
			dateTime = request.POST['wdate'].split(' ')
			w = Workshop.objects.get(pk=rid)
			
			#check if date time chenged or not
			if w.status == 1 and (str(w.wdate) != dateTime[0] or str(w.wtime)[0:5] != dateTime[1]):
				w.status = 4
			w.organiser_id = user.id
			w.academic_id = request.POST['academic']
			w.language_id = request.POST['language']
			w.foss_id = request.POST['foss']
			w.wdate = dateTime[0]
			w.wtime = dateTime[1]
			w.skype = request.POST['skype']
			w.save()
			return HttpResponseRedirect("/events/workshop/pending/")
		
		context = {'form':form, }
		return render(request, 'events/templates/workshop/form.html', context)
	else:
		context = {}
		record = Workshop.objects.get(id = rid)
		context.update(csrf(request))
		context['form'] = WorkshopForm(instance = record)
		context['instance'] = record
		return render(request, 'events/templates/workshop/form.html', context)

def workshop_list(request, status):
	""" Organiser index page """
	user = request.user
	if not (user.is_authenticated() and ( is_organiser(user) or is_resource_person(user) or is_event_manager(user))):
		raise Http404('You are not allowed to view this page!')
		
	status_dict = {'pending': 0, 'approved' : 1, 'completed' : 2, 'rejected' : 3, 'reschedule' : 1}
	if status in status_dict:
		context = {}
		if is_event_manager(user):
			workshops = Workshop.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
		elif is_resource_person(user):
			workshops = Workshop.objects.filter(academic__in = AcademicCenter.objects.filter(state__in = State.objects.filter(resourceperson__user_id=user)), status = status_dict[status])
		elif is_organiser(user):
			workshops = Workshop.objects.filter(organiser_id=user, status = status_dict[status])
			
		context['collection'] = workshops
		context['status'] = status
		context['can_manage'] = user.groups.filter(Q(name="Event Manager") |  Q(name="Resource Person"))
		context.update(csrf(request))
		return render(request, 'events/templates/workshop/index.html', context)
	else:
		raise Http404('Page not found !!')

@login_required
@csrf_exempt
def workshop_approvel(request, rid):
	""" Resource person: confirm or reject workshop """
	user = request.user
	try:
		w = Workshop.objects.get(pk=rid)
		if request.GET['status'] == 'accept':
			status = 1
		if request.GET['status'] == 'reject':
			status = 3
	except:
		raise Http404('Page not found !!')

	if not (user.is_authenticated() and w.academic.state in State.objects.filter(resourceperson__user_id=user) and ( is_event_manager(user) or is_resource_person(user))):
		raise PermissionDenied('You are not allowed to view this page!')
	
	w.status = status
	w.appoved_by_id = user.id
	#todo: add workshop code
	w.save()
	return HttpResponseRedirect('/events/workshop/approved/')

@login_required
def workshop_permission(request):
	user = request.user
	permissions = Permission.objects.select_related().all()
	form = WorkshopPermissionForm()
	if request.method == 'POST':
		form = WorkshopPermissionForm(request.POST)
		if form.is_valid():
			wp = Permission()
			wp.permissiontype_id = form.cleaned_data['permissiontype']
			wp.user_id = form.cleaned_data['user']
			wp.state_id = form.cleaned_data['state']
			wp.assigned_by_id = user.id
			if form.cleaned_data['district']:
				wp.district_id = form.cleaned_data['district']
			if form.cleaned_data['institute']:
				wp.institute_id = form.cleaned_data['institute']
			elif form.cleaned_data['institutiontype']:
				wp.institute_type_id = form.cleaned_data['institutiontype']
			elif form.cleaned_data['university']:
				wp.university_id = form.cleaned_data['university']
			wp.save()
			return HttpResponseRedirect("/events/workshop/permission/")
	
	context = {}
	context.update(csrf(request))
	context['form'] = form
	context['collection'] = permissions
	return render(request, 'events/templates/accessrole/workshop_permission.html', context)
	
@login_required
def accessrole(request):
	user = request.user
	state =  list(AcademicCenter.objects.filter(state__in = Permission.objects.filter(user=user, permissiontype_id=1).values_list('state_id')).values_list('id'))
	district = list(AcademicCenter.objects.filter(district__in = Permission.objects.filter(user=user, permissiontype_id=2, district_id__gt=0).values_list('district_id')).values_list('id'))
	university = list(AcademicCenter.objects.filter(university__in = Permission.objects.filter(user=user, permissiontype_id=3, university_id__gt=0).values_list('university_id')).values_list('id'))
	institution_type = list(AcademicCenter.objects.filter(institution_type__in = Permission.objects.filter(user=user, permissiontype_id=4, institute_type_id__gt=0).values_list('institute_type_id')). values_list('id'))
	institute = list(AcademicCenter.objects.filter(id__in = Permission.objects.filter(user=user, permissiontype_id=5, institute_id__gt=0).values_list('institute_id')).values_list('id'))
	all_academic_ids = list(set(state) | set(district) | set(university) | set(institution_type) | set(institute)) 
	workshops = Workshop.objects.filter(academic__in = all_academic_ids)
	context = {'collection':workshops}
	return render(request, 'events/templates/accessrole/workshop_accessrole.html', context)

def xmlparse(request):
	#path = "{0}/app_name/book.xml".format(
	#	settings.PROJECT_ROOT)
	path = "/home/deer/test.xml";
	xmlDoc = open(path, 'r')
	xmlDocData = xmlDoc.read()
	xmlDocTree = etree.XML(xmlDocData)

	for studentDetails in xmlDocTree.iter('detail'):
		firstname = studentDetails[0].text
		lastname = studentDetails[1].text
		gender =  studentDetails[2].text
		age = studentDetails[3].text
		email = studentDetails[4].text
		permanent_address = studentDetails[5].text
		city = studentDetails[6].text
		country = studentDetails[7].text
		department = studentDetails[8].text

	return HttpResponse('XML file read Done!')
	


#Ajax Request and Responces
@csrf_exempt
def ajax_ac_state(request):
	""" Ajax: Get University, District, City based State selected """
	if request.method == 'POST':
		state = request.POST.get('state')
		data = {}
		if request.POST.get('fields[district]'):
			district = District.objects.filter(state=state)
			tmp = ''
			for i in district:
				tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
				
			if(tmp):
				data['district'] = '<option value = None> -- None -- </option>'+tmp
			else:
				data['district'] = tmp
			
		if request.POST.get('fields[city]'):
			city = City.objects.filter(state=state)
			tmp = ''
			for i in city:
				tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
				
			if(tmp):
				data['city'] = '<option value = None> -- None -- </option>'+tmp
			else:
				data['city'] = tmp
			
		if request.POST.get('fields[university]'):
			university = University.objects.filter(state=state)
			tmp = ''
			for i in university:
				tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
			if(tmp):
				data['university'] = '<option value = None> -- None -- </option>'+tmp
			else:
				data['university'] = tmp
		
		return HttpResponse(json.dumps(data), mimetype='application/json')
		
@csrf_exempt
def ajax_ac_location(request):
	""" Ajax: Get the location based on district selected """
	if request.method == 'POST':
		district = request.POST.get('district')
		location = Location.objects.filter(district=district)
		tmp = '<option value = None> -- None -- </option>'
		for i in location:
			tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
		return HttpResponse(json.dumps(tmp), mimetype='application/json')

@csrf_exempt
def ajax_district_data(request):
	""" Ajax: Get the location based on district selected """
	data = {}
	if request.method == 'POST':
		tmp = ''
		district = request.POST.get('district')
		print district
		print "ddddddddddddd"
		if request.POST.get('fields[location]'):
			location = Location.objects.filter(district_id=district)
			tmp = '<option value = None> -- None -- </option>'
			for i in location:
				tmp +='<option value='+str(i.id)+'>'+i.name+'</option>'
			data['location'] = tmp
		
		if request.POST.get('fields[institute]'):
			collages = AcademicCenter.objects.filter(district=district)
			tmp = '<option value = None> -- None -- </option>'
			for i in collages:
				tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
			data['institute'] = tmp
		
	return HttpResponse(json.dumps(data), mimetype='application/json')

@csrf_exempt
def ajax_ac_pincode(request):
	""" Ajax: Get the pincode based on location selected """
	if request.method == 'POST':
		location = request.POST.get('location')
		location = Location.objects.get(pk=location)
		return HttpResponse(json.dumps(location.pincode), mimetype='application/json')

@csrf_exempt
def ajax_district_collage(request):
	""" Ajax: Get the Colleges (Academic) based on District selected """
	if request.method == 'POST':
		district = request.POST.get('district')
		collages = AcademicCenter.objects.filter(district=district)
		tmp = '<option value = None> -- None -- </option>'
		for i in collages:
			tmp +='<option value='+str(i.id)+'>'+i.institution_name+'</option>'
		return HttpResponse(json.dumps(tmp), mimetype='application/json')

@csrf_exempt
def test(request):
	print "*******"
	url = request.build_absolute_uri()
	parsed_uri = urlparse(url)
	uri=parsed_uri
	domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
	print uri.netloc
	print domain
