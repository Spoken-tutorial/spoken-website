# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.db.models import Q
from django.contrib.auth.models import User
from django.urls import reverse
from django.db import IntegrityError
# Python imports
from datetime import datetime,date
import csv
import json
import random
import uuid 
# Spoken imports
from .models import *
from .forms import *
from .helpers import *
from .templatetags.trainingdata import registartion_successful, get_event_details, get_user_detail
from creation.models import TutorialResource, Language, FossCategory
from events.decorators import group_required
from events.models import *
from events.views import is_resource_person, is_administrator, get_page, id_generator, is_event_manager
from events.filters import ViewEventFilter, PaymentTransFilter, TrEventFilter
from cms.sortable import *
from cms.views import create_profile, send_registration_confirmation, get_confirmation_code
from cms.models import Profile
from certificate.views import _clean_certificate_certificate
from django.http import HttpResponse
from django.template import RequestContext
from .filters import CompanyFilter
import os, sys
from string import Template
import subprocess
from events.certificates import get_organization, get_signature
from health_app.models import TopicCategory, HNContributorRole, HNLanguage
from spoken.config import HN_API

#pdf generate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER
from PyPDF2 import PdfFileWriter, PdfFileReader
from io import BytesIO
from django.conf import settings
from donate.models import *

import csv
import requests

class TrainingEventCreateView(CreateView):
	form_class = CreateTrainingEventForm
	model = TrainingEvents
	template_name = "create_event.html"
	success_url = "/software-training/"

	@method_decorator(group_required("Resource Person"))
	def get(self, request, *args, **kwargs):
		form = self.form_class()
		context = {'form': self.form_class()}
		context['pdp_fee']=settings.PDP_FEE
		context['cdp_fee']=settings.CDP_FEE
		fossess = FossCategory.objects.filter(id__in=CourseMap.objects.filter(category=0, test=1).values('foss_id'))
		context['fossess']=fossess
		context['DEFAULT_ILW_HOST_COLLEGE']=DEFAULT_ILW_HOST_COLLEGE
		return render(self.request, self.template_name, context)

	def form_valid(self, form, **kwargs):
		
		self.object = form.save(commit=False)
		self.object.entry_user = self.request.user
		self.object.Language_of_workshop = Language.objects.get(id=22)
		ilw_course = form.cleaned_data.get('ilw_course', '-')
		foss_data = form.cleaned_data.get('foss_data', [])
		course = ILWCourse.objects.create(name = ilw_course)
		if foss_data:
			course.foss.set(foss_data)
		self.object.course = course
		self.object.save()
		messages.success(self.request, "New Event created successfully.")
		return HttpResponseRedirect(self.success_url)
	
	def form_invalid(self, form):
		context = self.get_context_data(form=form)
		return self.render_to_response(context)

#ILW main page
class TrainingEventsListView(ListView):
	model = TrainingEvents
	raw_get_data = None
	header = None
	collection = None

	def dispatch(self, *args, **kwargs):
		self.status = self.kwargs['status']
		today = date.today()
		self.show_myevents = False
		if self.request.user:
			myevents = TrainingEvents.objects.filter(id__in=Participant.objects.filter(user_id=self.request.user.id).values('event_id'))
			if myevents:
				self.show_myevents = True

		if self.status == 'completed':
			self.events = TrainingEvents.objects.filter(event_end_date__lt=today).order_by('-event_end_date')
		if self.status == 'ongoing':
			self.events = TrainingEvents.objects.filter(event_end_date__gte=today).order_by('registartion_end_date')
		if self.status == 'myevents':
			participant = Participant.objects.filter(
				Q(payment_status__status=1)|Q(registartion_type__in=(1,3)),
				user_id=self.request.user.id)
			self.events = participant

		self.raw_get_data = self.request.GET.get('o', None)
		self.queryset = get_sorted_list(
			self.request,
			self.events,
			self.header,
			self.raw_get_data
		)

		self.collection= ViewEventFilter(self.request.GET, queryset=self.queryset, user=self.request.user)
		return super(TrainingEventsListView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(TrainingEventsListView, self).get_context_data(**kwargs)
		context['form'] = self.collection.form
		page = self.request.GET.get('page')
		collection = get_page(self.collection.qs, page)
		context['collection'] =  collection
		context['ordering'] = get_field_index(self.raw_get_data)
		context['status'] =  self.status
		context['events'] =  self.events
		context['show_myevents'] = self.show_myevents
		context['ILW_ONLINE_TEST_URL'] = settings.ILW_ONLINE_TEST_URL
		context['HN_API'] = HN_API
		
		if self.request.user:
			context['user'] = self.request.user
		return context

def _validate_parameters(parameter, value):
	if value is None:
		return False
	if parameter == 'source':
		return value.lower() == 'deet'
	if parameter == 'phone':
		return value.isnumeric() and len(value) < 12
	if parameter == 'event_id':
		return value.isnumeric()
	return True

@csrf_exempt
def register_user(request):
	form = RegisterUser()
	template_name = "register_user.html"
	context = {}
	context['form']= form
	context['source'] = None
	context['email'] = None
	context['callbackurl'] = None
	
	if request.user.is_authenticated():
		user = request.user
		profile = Profile.objects.get(user=user)
		form.fields["name"].initial = user.get_full_name()
		form.fields["email"].initial = getattr(user, 'email')
		form.fields["phone"].initial = profile.phone
		form.fields['email'].widget.attrs['readonly'] = True
		if user.profile_set.all():
			try:
				form.fields["state"].initial = getattr(user.profile_set.all()[0], 'state')
				college = user_college(request.user)
				context['user_college'] = college
			except Exception as e:
				raise e
	if request.method == 'GET':
		source = request.GET.get('source', None)
		foss = request.GET.get('foss', None)
		event_id = request.GET.get('event_id', None)
		email = request.GET.get('email', None)
		name = request.GET.get('name', None)
		gender = request.GET.get('gender', None)
		phone = request.GET.get('phone', None)
		callbackurl = request.GET.get('callbackurl', None)
		event_id = request.GET.get('event_id')
		if not _validate_parameters('source', source):
			return render(request, 'error.html', {'error': 'Invalid Source'})
		if not _validate_parameters('foss', foss):
			return render(request, 'error.html', {'error': 'No foss mentioned'})
		if not _validate_parameters('email', email):
			return render(request, 'error.html', {'error': 'No email mentioned'})
		if not _validate_parameters('name', name):
			return render(request, 'error.html', {'error': 'No name mentioned'})
		if not _validate_parameters('gender', gender):
			return render(request, 'error.html', {'error': 'No gender mentioned'})
		if not _validate_parameters('phone', phone):
			return render(request, 'error.html', {'error': 'Invalid Phone number'})
		if not _validate_parameters('event_id', event_id):
			return render(request, 'error.html', {'error': 'Invalid Event'})
		if not _validate_parameters('callbackurl', callbackurl):
			return render(request, 'error.html', {'error': 'Callback url not mentioned'})
		if event_id:
			event_register = TrainingEvents.objects.get(id=event_id)
			if event_register.event_type == 'HN':
				ExternalCourseMap.objects.filter(foss=foss)
			else:
				langs = Language.objects.filter(id__in =
					TutorialResource.objects.filter(
					tutorial_detail__foss = event_register.foss, status=1).exclude(
						language=event_register.Language_of_workshop).values('language').distinct())
			context["langs"] = langs
			form.fields["foss_language"].queryset = langs
			gst = float(event_register.event_fee)* 0.18
			context["gst"] = gst
			form.fields["amount"].initial = float(event_register.event_fee) + gst
			form.fields["amount"].widget.attrs['readonly'] = True
			context['event_obj']= event_register
			form.fields['name'].initial = name
			form.fields['phone'].initial = phone
			if gender.lower() == 'female':
				form.fields['gender'].initial = 'F'
			elif gender.lower() == 'male':
				form.fields['gender'].initial = 'M'
			else:
				form.fields['gender'].initial = 'O'
			form.fields['name'].widget.attrs['readonly'] = True
			form.fields['phone'].widget.attrs['readonly'] = True
			form.fields['gender'].widget.attrs['readonly'] = True
			context['source'] = source
			context['email'] = email
			context['callbackurl'] = callbackurl
	if request.method == 'POST':
		event_id = request.POST.get("event_id_info")
		if event_id:
			event_register = TrainingEvents.objects.get(id=event_id)
			fosses = event_register.course.foss.all()
			if event_register.event_type == 'HN':
				hn_categories = [x.external_course for x in ExternalCourseMap.objects.filter(foss__in=fosses)]
				topic_categories = TopicCategory.objects.filter(category_id__in=hn_categories).values_list('topic_category_id', flat=True)
				languages = HNContributorRole.objects.filter(topic_cat_id__in=topic_categories).values_list('language_id', flat=True)
				langs = HNLanguage.objects.filter(lan_id__in=languages).distinct()
				context["language_hn"] = langs
				form.fields["language_hn"].queryset = langs
			else:
				langs = Language.objects.filter(id__in = 
					TutorialResource.objects.filter(
					tutorial_detail__foss__in = fosses, status=1).exclude(
						language=event_register.Language_of_workshop).values('language').distinct())
				context["langs"] = langs
			form.fields["foss_language"].queryset = langs
			gst = float(event_register.event_fee)* 0.18
			context["gst"] = gst
			form.fields["amount"].initial = float(event_register.event_fee) + gst
			form.fields["amount"].widget.attrs['readonly'] = True
			context["fossess"] = [foss.id for foss in event_register.course.foss.all()]
			context['event_obj']= event_register
	return render(request, template_name,context)

@csrf_exempt
def reg_success(request, user_type):
	context = {}
	template_name = "reg_success.html"
	if request.method == 'POST':
		name = request.POST.get('name')
		email = request.POST.get('email')
		phone = request.POST.get('phone')
		event_obj = request.POST.get('event')
		source = request.POST.get('source')
		callbackurl = request.POST.get('callbackurl')
		city = request.POST.get('city')
		company = request.POST.get('company')
		new_company = request.POST.get('new_company')
		event = TrainingEvents.objects.get(id=event_obj)
		
		form = RegisterUser(request.POST)
		event_type = request.POST.get('event_type', '')
		if form.is_valid():
			form_data = form.save(commit=False)
			form_data.user = request.user
			form_data.event = event

			if source == 'deet':
				form_data.source = source
			if not event_type in ['PDP', 'CDP', 'HN']:
				try:
					college = request.POST.get('college')
					form_data.college = AcademicCenter.objects.get(Q(institution_name=college))
				except Exception as e:
					form_data.college = AcademicCenter.objects.get(id=request.POST.get('dropdown_college'))	
			else:
				city_obj = City.objects.get(id=city)	
				form_data.city = city_obj
				form_data.college = AcademicCenter.objects.get(id=request.POST.get('college'))	
				if company:
					comp_obj = Company.objects.get(id=company)
					form_data.company = comp_obj
				else:
					try:
						company=Company.objects.create(name=new_company, added_by=request.user)
						form_data.company = company
					except IntegrityError:
						pass
			user_data = is_user_paid(form_data.college.id)
			if user_data:
				form_data.registartion_type = 1 #Subscribed College
			else:
				form_data.registartion_type = 2 #Manual reg- paid 500

			part = Participant.objects.filter(
				Q(payment_status__status = 1)|Q(registartion_type__in  = (1,3)),
				user = request.user, event = form_data.event)

			if part.exists():
				messages.success(request, "You have already registered for this event.")
				return redirect('training:list_events', status='myevents')
			else :
				form_data.save()
			event_name = event.event_name
			userprofile = Profile.objects.get(user=request.user)
			userprofile.phone = phone
			userprofile.save()
			if user_type == 'paid':
				# if user is already a paid user -> render reg_success.html showing registration success 
				context = {'participant_obj':form_data}
				if form_data.source == 'deet':
					json = {'id': f'n{form_data.id}', 'name': form_data.name,
						'email': form_data.email, 'paid college': True,
						'amount': 0.0, 'status': 1}
					requests.post(callbackurl, json)
				return render(request, template_name, context)
			else:
				# if user has made payment from ILW interface -> return Participant form
				return form_data
		else:
			messages.warning(request, 'Invalid form payment request 1.')
			return redirect('training:list_events', status='ongoing' )


class EventPraticipantsListView(ListView):
	model = Participant
	@method_decorator(group_required("Resource Person"))
	def dispatch(self, *args, **kwargs):
		self.eventid = self.kwargs['eventid']
		self.queryset = Participant.objects.filter(event_id=self.eventid)
		self.event = TrainingEvents.objects.get(id=self.eventid)
		today = date.today()
		self.training_status = 0 #ongoing

		if self.event.event_end_date < today:
			self.training_status = 1 #completed
		return super(EventPraticipantsListView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(EventPraticipantsListView, self).get_context_data(**kwargs)
		context['training_status']= self.training_status
		context['eventid']= self.eventid
		context['event']= self.event
		return context


def edit_training_event(request, pk):
	event = get_object_or_404(TrainingEvents, id=pk)
	fossess = FossCategory.objects.filter(id__in=CourseMap.objects.filter(category=0, test=1).values('foss_id'))
	context = {}
	context['fossess']=fossess
	selected_foss = event.course and event.course.foss.all().values_list('id', flat=True)
	context['selected_foss'] = selected_foss
	
	if request.method == "POST":
		form = EditTrainingEventForm(request.POST, instance=event)
		if form.is_valid():
			form.save(commit=True)
			messages.add_message(request, messages.SUCCESS, f"event updated successfully")
			return redirect(reverse('training:edit_event', args=[event.id]))
	else:
		form = EditTrainingEventForm(instance=event)
	context['form']=form
	return render(request, 'edit_event.html',context)

class EventUpdateView(UpdateView):
	model = TrainingEvents
	form_class = CreateTrainingEventForm
	success_url = "/training/event/rp/ongoing/"


#used to display evnets to mngrs under dashboard link
def listevents(request, role, status):
	today=date.today()
	context = {}
	user = request.user
	if not (user.is_authenticated() and (is_resource_person(user) or is_administrator(user))):
		raise PermissionDenied()

	if (not role ) or (not status):
		raise PermissionDenied()

	states = State.objects.filter(resourceperson__user_id=user, resourceperson__status=1)
	TrMngerEvents = TrainingEvents.objects.filter(state__in=states).order_by('-event_start_date')
	

	status_list = {'ongoing': 0, 'completed': 1, 'closed': 2, 'expired': 3}
	roles = ['rp', 'em']
	if role in roles and status in status_list:
		if status == 'ongoing':
			queryset = TrMngerEvents.filter(training_status__lte=1, event_end_date__gte=today)
		elif status == 'completed':
			queryset =TrMngerEvents.filter(training_status=1, event_end_date__lt=today)
		elif status == 'closed':
			queryset = TrMngerEvents.filter(training_status=2)
		elif status == 'expired':
			queryset = TrMngerEvents.filter(training_status=0, event_end_date__lt=today)

		header = {
		1: SortableHeader('#', False),
		2: SortableHeader(
		  'state__name',
		  True,
		  'State'
		),
		3: SortableHeader(
		  'host_college__academic_code',
		  True,
		  'Code'
		),
		4: SortableHeader(
		  'host_college__institution_name',
		  True,
		  'Institution'
		),
		5: SortableHeader('foss__foss', True, 'Foss Name'),
		6: SortableHeader(
		  'event_coordinator_name',
		  True,
		  'Coordinator'
		),
		7: SortableHeader(
		  'registartion_end_date',
		  True,
		  'Registration Period'
		),
		8: SortableHeader(
		  'event_start_date',
		  True,
		  'Event Start Date'
		),
		9: SortableHeader(
		  'event_end_date',
		  True,
		  'Event End Date'
		),
		10: SortableHeader('Participant Count', True),
		11: SortableHeader('Action', False)
		}
		event_type = request.GET.get('event_type', None)
		pcount, mcount, fcount = get_all_events_detail(queryset, status, event_type)
		raw_get_data = request.GET.get('o', None)
		queryset = get_sorted_list(
			request,
			queryset,
			header,
			raw_get_data
		)
		collection= TrEventFilter(request.GET, queryset=queryset, user=user)
      

	else:
		raise PermissionDenied()

	context['form'] = collection.form
	page = request.GET.get('page')
	collection = get_page(collection.qs, page)
	context['collection'] =  collection
	context['role'] = role
	context['status'] = status
	context['header'] = header
	context['today'] = date.today()
	context['ordering'] = get_field_index(raw_get_data)
	context['pcount'] = pcount
	context['mcount'] = mcount
	context['fcount'] = fcount

	return render(request,'event_status_list.html',context)


def close_event(request, pk):
	context = {}
	user = request.user
	if not (user.is_authenticated() and is_resource_person(user)):
		raise PermissionDenied()
	
	event = TrainingEvents.objects.get(id=pk)
	if event:
		event.training_status = 2 #close event
		event.save()
		messages.success(request, 'Event has been closed successfully')
	else:
		messages.error(request, 'Request not sent.Please try again.')
	return HttpResponseRedirect("/training/event/rp/completed/")


def approve_event_registration(request, pk):
	context = {}
	user = request.user
	if not (user.is_authenticated() and is_resource_person(user)):
		raise PermissionDenied()
	
	event = TrainingEvents.objects.get(id=pk)
	if event:
		event.training_status = 1 #approve registraions
		event.save()
		messages.success(request, 'Registrations approved successfully')
	else:
		messages.error(request, 'Request not sent.Please try again.')
	return HttpResponseRedirect("/training/event/rp/ongoing/")


class ParticipantCreateView(CreateView):
	form_class = UploadParticipantsForm

	@method_decorator(group_required("Resource Person"))
	def dispatch(self, *args, **kwargs):
		if 'eventid' in kwargs:
			try:
				self.event = TrainingEvents.objects.get(pk=kwargs['eventid'])
			except:
				messages.error(self.request, 'Event not found')
				return HttpResponseRedirect(reverse("training:create_event"))
			if not self.event.training_status == 0:
					messages.error(self.request,'Upoad via CSV is not allowed as Event registration is closed')
		return super(ParticipantCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(ParticipantCreateView, self).get_context_data(**kwargs)
		context['event']= self.event
		return context

	def form_valid(self, form):
		count = 0
		csv_file_data = form.cleaned_data['csv_file']
		registartion_type = form.cleaned_data['registartion_type']			
		if registartion_type == 2:
			# 3 - Manual Registration via CSV(option not visible outside)
			registartion_type = 3
		rows_data = csv.reader(csv_file_data, delimiter=',', quotechar='|')
		csv_error = False
		user_errors = []
		for i, row in enumerate(rows_data):
			user = self.get_create_user(row)
			if user:
				try:
					college = AcademicCenter.objects.get(academic_code=row[6])
				except AcademicCenter.DoesNotExist:
					csv_error = True
					messages.add_message(self.request, messages.ERROR, "Row: "+ str(i+1) + " Institution name " + row[6] + " does not exist."+" Participant "+ row[2] + " was not created.")
					continue
				
				if registartion_type == 1:
					if not(is_college_paid(college.id)):
						messages.add_message(self.request, messages.ERROR, "Row: "+ str(i+1) + " Institution " + row[6] + " is not a Paid college."+" Participant "+ row[2] + " was not created.")
						continue

				try:
					foss_language = Language.objects.get(name=row[7].strip())	
				except :
					messages.add_message(self.request, messages.ERROR, "Row: "+ str(i+1) + " Language name " + row[7] + " does not exist."+" Participant "+ row[2] + " was not created.")
					continue

				participant = Participant.objects.filter(email=row[2].strip(),event = self.event)
				if participant.exists() and registartion_successful(user, self.event):
					messages.add_message(self.request, messages.WARNING, "Participant with email "+row[2]+" already registered for "+self.event.event_name)
					continue
				else:
					try:
						Participant.objects.create(
							name = row[0]+" "+row[1], 
							email = row[2].strip(), 
							gender = row[3], 
							amount = row[4], 
							event = self.event, 
							user = user, 
							state = college.state, 
							college = college,
							foss_language = foss_language,
							registartion_type = registartion_type,
							reg_approval_status = 1
							)
						count = count + 1
					except :
						csv_error = True
						messages.add_message(self.request, messages.ERROR, "Could not create participant having email id" + row[2])
			else:
				user_errors.append(row[2])
		if user_errors:
			user_errors = ', '.join(user_errors)
			messages.error(self.request, f"The participants with the following emails were not created. Please verify the email addresses: {user_errors}")
		if csv_error:
			messages.warning(self.request, 'Some rows in the csv file has errors and are not created.')
		if count > 0:
			messages.success(self.request, 'Successfully uploaded '+str(count)+" participants")
		return HttpResponseRedirect(reverse("training:upload_participants", kwargs={'eventid': self.event.pk}))


	def get_create_user(self, row):
		try:
			return User.objects.get(email=row[2].strip())
		except User.DoesNotExist:
			user = User(username=row[2], email=row[2].strip(), first_name=row[0], last_name=row[1])
			user.set_password(row[0]+'@ST'+str(random.random()).split('.')[1][:5])
			# confirmation_code = get_confirmation_code()
			confirmation_code = send_registration_confirmation(user)
			if confirmation_code:
				user.save()
				create_profile(user, '', confirmation_code)
				return user
			return None


def mark_reg_approval(pid, eventid):
    participant = Participant.objects.get(event_id =eventid, id=pid)
    participant.reg_approval_status = 1
    participant.save()

class EventAttendanceListView(ListView):
	queryset = ""
	unsuccessful_payee = ""
	paginate_by = 500
	success_url = ""

	def dispatch(self, *args, **kwargs):
		self.event = TrainingEvents.objects.get(pk=kwargs['eventid'])
		main_query = Participant.objects.filter(event_id=kwargs['eventid'])

		self.queryset =	main_query.filter(Q(payment_status__status=1)| Q(registartion_type__in=(1,3)) | Q(payment_status__transaction__order_status="CHARGED"))
		self.unsuccessful_payee = main_query.filter(Q(payment_status__status__in=(0,2)) &  ~Q(payment_status__transaction__order_status="CHARGED"))
		if self.event.training_status == 1:
			self.queryset = main_query.filter(reg_approval_status=1)

		if self.event.training_status == 2:
			self.queryset = self.event.eventattendance_set.all()
		return super(EventAttendanceListView, self).dispatch(*args, **kwargs)


	def get_context_data(self, **kwargs):
		context = super(EventAttendanceListView, self).get_context_data(**kwargs)
		
		context['event'] = self.event
		context['eventid'] = self.event.id
		context['unsuccessful_payee'] = self.unsuccessful_payee
		return context

	def post(self, request, *args, **kwargs):
		self.object = None
		self.user = request.user
		eventid = kwargs['eventid']
		attendance_type = request.POST.get('event_status', None)

		if attendance_type == 'attend':
			if request.POST and 'user' in request.POST:
				marked_participant = request.POST.getlist('user', None)
				# delete un marked record if exits
				EventAttendance.objects.filter(event_id =eventid).exclude(participant_id__in = marked_participant).delete()
				# insert new record if not exits
				for record in marked_participant:
					event_attend = EventAttendance.objects.filter(event_id =eventid, participant_id = record)
					if not event_attend.exists():
						EventAttendance.objects.create(event_id =eventid, participant_id = record)
					#print marked_participant
				success_url = '/training/event/rp/completed'
			else:
				EventAttendance.objects.filter(event_id = eventid).delete()
				success_url = '/training/event/rp/completed'
		
		elif attendance_type == 'reg':
			if request.POST and 'user_reg' in request.POST:
				marked_registrations = request.POST.getlist('user_reg', None)
				# delete un marked record if exits
				remove_reg = Participant.objects.filter(event_id =eventid, reg_approval_status=1).exclude(id__in = marked_registrations).update(reg_approval_status=0)
				
				# insert new record if not exits
				for record in marked_registrations:
					reg_attend = Participant.objects.filter(event_id =eventid, id = record, reg_approval_status=1)
					if not reg_attend.exists():
						mark_reg_approval(record, eventid)
					#print marked_registrations
				success_url = '/training/event/rp/ongoing'
			else:
				Participant.objects.filter(event_id =eventid).update(reg_approval_status=0)
				success_url = '/training/event/rp/ongoing'
		return HttpResponseRedirect(success_url)



@csrf_exempt
def ajax_check_college(request):
	college_id = request.POST.get("college_id")
	user_details = is_user_paid(int(college_id))
	check = user_details
	return HttpResponse(json.dumps(check), content_type='application/json')


def get_create_user(row):
		try:
			return User.objects.get(email=row[2].strip())
		except User.DoesNotExist:
			user = User(username=row[2], email=row[2].strip(), first_name=row[0], last_name=row[1])
			user.set_password(row[0]+'@ST'+str(random.random()).split('.')[1][:5])
			user.save()
			create_profile(user, '')
			send_registration_confirmation(user)
			return user

from io import TextIOWrapper
from django.contrib.auth.decorators import login_required
@login_required
def upload_college_details(request):
	form = UploadCollegeForm
	context ={}
	context['form'] = form
	count = 0
	csv_error = ''
	if request.POST:
		csv_file_data = TextIOWrapper(request.FILES['csv_file'], encoding='utf-8')
		rows_data = csv.reader(csv_file_data, delimiter=',')
		for i, row in enumerate(rows_data):
			user = get_create_user(row)
			try:
				college = AcademicCenter.objects.get(academic_code=row[2])
			except AcademicCenter.DoesNotExist:
				csv_error = True
				messages.add_message(request, messages.ERROR, "Row: "+ str(i+1) + " College" + row[2] + "  does not exist.")
				continue
			try:
				state = State.objects.get(name=row[1])
			except State.DoesNotExist:
				csv_error = True
				messages.add_message(request, messages.ERROR, "Row: "+ str(i+1) + " State " + row[1] + " does not exist."+" College "+ row[2] + " was not added.")
				continue
			subscription = ''
			payment_status = ''
			college_type = ''
			if '1 year' in row[7]:
				subscription = '365'
			if '6 months' in row[7]:
				subscription = '180'
			if row[11] == 'Engineering':
				college_type = 'Engg'
			day,mon,year = row[9].split('/')
			payment_date = datetime(year=int(year), month=int(mon), day=int(day))
			try:
				ac_payment_new = AcademicPaymentStatus.objects.create(
					state = state,
	  				academic = college,
					name_of_the_payer = row[3],
					email = row[4],
					phone = row[5],
					amount = row[6],
					subscription =  subscription,
					transactionid = row[8],
					payment_date = payment_date,
					payment_status = row[10],
					college_type = college_type,
					pan_number = row[12],
					gst_number = row[13],
					customer_id = row[14],
					invoice_no = row[15],
					remarks = row[16],
					entry_date = payment_date,
					entry_user = request.user
					)
				try:
					add_Academic_key(ac_payment_new, subscription)
				except :
					messages.add_message(request, messages.ERROR, " Academic key for " + row[2]+" already exists")
				count = count + 1
			except :
				academic_centre = AcademicPaymentStatus.objects.filter(
					academic=college, transactionid= row[9], payment_date = payment_date)
				if academic_centre.exists():
					messages.add_message(request, messages.WARNING, "Institution "+row[2]+" already made payment on "+row[9])
				else:	
					csv_error = True
					messages.add_message(request, messages.ERROR, " Academic payment for " + row[2]+" already exists")
		if csv_error:
			messages.warning(request, 'Some rows in the csv file has errors and are not created.')
		if count > 0:
			messages.success(request, 'Successfully uploaded '+str(count)+" Institutions")
			return render(request,'upload_college_details.html',context)
	else:
		return render(request,'upload_college_details.html',context)

	return render(request,'upload_college_details.html',context)

def add_Academic_key(ac_pay_status_object, subscription):
	u_key = uuid.uuid1()
	hex_key = u_key.hex

	Subscription_time = int(subscription)
	expiry_date = ac_pay_status_object.payment_date + timedelta(days=Subscription_time)

	ac_key = AcademicKey()      
	ac_key.ac_pay_status = ac_pay_status_object
	ac_key.academic = ac_pay_status_object.academic
	ac_key.u_key = u_key
	ac_key.hex_key = hex_key
	ac_key.expiry_date = expiry_date
	ac_key.save()


class FDPTrainingCertificate(object):
  def custom_strftime(self, format, t):
    return t.strftime(format).replace('{S}', str(t.day) + self.suffix(t.day))

  def suffix(self, d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

  def create_fdptraining_certificate(self, event, user):
    participantname = f"{user.first_name} {user.last_name}"
    training_start = event.event_start_date
    
    response = HttpResponse(content_type='application/pdf')
    filename = (participantname+'-'+"-Participant-Certificate").replace(" ", "-");

    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = BytesIO ()
    imgDoc = canvas.Canvas(imgTemp)

    # Title
    imgDoc.setFont('Helvetica', 35, leading=None)
    if event.event_type != "INTERN":
        imgDoc.drawCentredString(405, 470, "Certificate of Participation")
        # Draw image on Canvas and save PDF in buffer
        imgPath = get_signature(training_start)
        imgDoc.drawImage(imgPath, 600, 100, 150, 76)

    #password
    certificate_pass = ''
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)

    #paragraphe
    text = get_training_certi_text(event, user)

    centered = ParagraphStyle(name = 'centered',
      fontSize = 16,
      leading = 30,
      alignment = 0,
      spaceAfter = 20
    )

    p = Paragraph(text, centered)
    p.wrap(650, 200)
    p.drawOn(imgDoc, 4.2 * cm, 5.5 * cm)

    imgDoc.save()
    # Use PyPDF to merge the image-PDF into the template
    template_path = get_ilw_certificate(event, 'training')
    page = PdfFileReader(open(template_path,"rb")).getPage(0)
    overlay = PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)

    #stream to browser
    outputStream = response
    output.write(response)
    outputStream.close()

    return response


class EventTrainingCertificateView(FDPTrainingCertificate, View):
  template_name = ""
  
  def dispatch(self, *args, **kwargs):
    return super(EventTrainingCertificateView, self).dispatch(*args, **kwargs)

  def post(self, request, *args, **kwargs):
    eventid = self.request.POST.get("eventid")
    event = TrainingEvents.objects.get(id=eventid)
    participantname = self.request.user.first_name+" "+self.request.user.last_name
    if event:
      return self.create_fdptraining_certificate(event, self.request.user)
    else:
      messages.error(self.request, "Permission Denied!")
    return HttpResponseRedirect("/")

class ParticipantTransactionsListView(ListView):
	model = PaymentTransaction
	raw_get_data = None
	header = None
	collection = None
	@method_decorator(group_required("Resource Person","Administrator"))
	def dispatch(self, *args, **kwargs):
		today = date.today()
		statenames = State.objects.filter(resourceperson__user_id=self.request.user, resourceperson__status=1).values('name')
		self.PaymentTransaction = PaymentTransaction.objects.filter(paymentdetail__state__in=statenames).order_by('-created')
		self.events = self.PaymentTransaction

		self.header = {
		1: SortableHeader('#', False),
		2: SortableHeader(
		  'paymentdetail__user__first_name',
		  True,
		  'First Name'
		),
		3: SortableHeader(
		  'paymentdetail__user__last_name',
		  True,
		  'Last Name'
		),
		4: SortableHeader(
		  'paymentdetail__email',
		  True,
		  'Email'
		),
		5: SortableHeader(
		  'paymentdetail__state',
		  True,
		  'State'
		),
		
		6: SortableHeader('transId', True, 'Transaction id'),
		7: SortableHeader('paymentdetail__user_id', True, 'UserId'),
		8: SortableHeader('refNo', True, 'Reference No.'),
		9: SortableHeader('status', True, 'Status'),
		10: SortableHeader('paymentdetail__purpose', True, 'Purpose'),
		11: SortableHeader('requestType', True, 'RequestType'),
		12: SortableHeader('amount', True, 'Amount'),
		13: SortableHeader('created', True, 'Entry Date'),
		14: SortableHeader('paymentdetail__user', True, 'Phone'),
		}

		self.raw_get_data = self.request.GET.get('o', None)
		self.purpose = self.request.GET.get('paymentdetail__purpose')		

		if self.purpose != 'cdcontent':
			self.events= self.events.filter().exclude(paymentdetail__purpose='cdcontent')

		self.queryset = get_sorted_list(
			self.request,
			self.events,
			self.header,
			self.raw_get_data
		)

		self.collection= PaymentTransFilter(self.request.GET, queryset=self.queryset, user=self.request.user)
		self.total_amount = self.collection.qs.filter(requestType='R').aggregate(Sum('amount'))
		return super(ParticipantTransactionsListView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(ParticipantTransactionsListView, self).get_context_data(**kwargs)
		context['form'] = self.collection.form
		page = self.request.GET.get('page')
		collection = get_page(self.collection.qs, page)
		context['collection'] =  collection
		context['header'] = self.header
		context['ordering'] = get_field_index(self.raw_get_data)
		context['events'] =  self.events
		context['total_amount']=self.total_amount
		if self.request.user:
			context['user'] = self.request.user
		return context


@csrf_exempt
def ajax_collage_event(request):
	""" Ajax: Get the Colleges (Academic) based on District selected """
	if request.method == 'POST':
		college = request.POST.get('college')
		print(college)
		events = TrainingEvents.objects.filter(host_college_id=college).order_by('event_name')
		print(events)
		tmp = '<option value = None> --------- </option>'
		if events:
			for i in events:
				tmp +='<option value='+str(i.id)+'>'+i.event_name+', '+i.event_type+'</option>'
		return HttpResponse(json.dumps(tmp), content_type='application/json')



@csrf_protect
@login_required
def participant_transactions(request, purpose):    
	user = User.objects.get(id=request.user.id)
	rp_states = ResourcePerson.objects.filter(status=1,user=user)
	context = {}

	if request.method == 'GET':
		form = TrainingManagerPaymentForm(user,request.GET)
		allpaydetails = get_transaction_details(request, purpose)	
		request_type = request.GET.get('request_type')
		if request_type == 'R':
			context['total'] = allpaydetails.aggregate(Sum('amount'))

	paginator = Paginator(allpaydetails, 25)
	page_number = request.GET.get('page', 1)
	page_obj = paginator.page(page_number)
	context['form'] = form
	context['user'] = user
	context['purpose'] = purpose
	context['page_obj'] = page_obj

	event_dict = {}
	if purpose != 'cdcontent':
		#fetch event details
		events_ids = list(page_obj.object_list.values_list('paymentdetail__purpose', flat=True))
		events = TrainingEvents.objects.filter(id__in=events_ids).select_related('course')
		for event in events:
			course = ', '.join(event.course.foss.all().values_list('foss', flat=True))
			event_dict[str(event.id)] = {'name': event.event_name, 'course': course, 'event_start_date': event.event_start_date, 'event_end_date': event.event_end_date}
	
	phone_dict = {}
	users = [x.paymentdetail.user.id for x in page_obj.object_list]
	profiles = Profile.objects.filter(user_id__in=users)
	for item in profiles:
		phone_dict[str(item.user_id)] = item.phone

	context['event_dict'] = event_dict
	context['phone_dict'] = phone_dict
	return render(request,'participant_transaction_list_new.html', context)



def transaction_csv(request, purpose):
# export statistics training data as csv
	collectionSet = None
	collection = get_transaction_details(request, purpose)

	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="training-statistics-data.csv"'

	writer = csv.writer(response)

	# header
	if purpose != 'cdcontent':
		writer.writerow(['Sr No', 'Event Details','Name', 'Email','State','User Id','Transaction Id',\
		'Reference No','Status','Request Type','Amount','Entry Created','Phone Number'])
	else:
		writer.writerow(['Sr No', 'Name', 'Email','State','User Id','Transaction Id',\
		'Reference No','Status','Request Type','Amount','Entry Created','Phone Number'])

	count = 0
	# records
	for record in collection:
		count=count+1
		phone = get_user_detail(record.paymentdetail.user)
		if purpose != 'cdcontent':
			event  = get_event_details(record.paymentdetail.purpose)
			writer.writerow([count,
				f"{event.event_name}, {', '.join(x.foss for x in event.course.foss.all())}",
	            record.paymentdetail.user.first_name+' '+record.paymentdetail.user.first_name,
	            record.paymentdetail.email,
	            record.paymentdetail.state,
	            record.paymentdetail.user_id,
	            record.transId,
	            record.refNo,
	            record.status,
	            record.requestType,
	            record.amount,
	            record.created,
	            phone])
		else:
			writer.writerow([count,
				record.paymentdetail.user.first_name+' '+record.paymentdetail.user.first_name,
				record.paymentdetail.email,
				record.paymentdetail.state,
				record.paymentdetail.user_id,
				record.transId,
				record.refNo,
				record.status,
				record.requestType,
				record.amount,
				record.created,
				phone])
	return response

def reopen_event(request, eventid):
	context = {}
	user = request.user
	if not (user.is_authenticated() and is_resource_person(user)):
		raise PermissionDenied()
	
	event = TrainingEvents.objects.get(id=eventid)
	if event:
		event.training_status = 0 #close event
		event.save()
		messages.success(request, 'Event reopened successfully. As the event date over you will find this entry under expired tab.')
	else:
		messages.error(request, 'Request not sent.Please try again.')
	return HttpResponseRedirect("/training/event/rp/completed/")


class EventParticipantsListView(ListView):
	queryset = None
	unsuccessful_payee = ""
	paginate_by = 500

	def get_queryset(self):
		event_id = self.kwargs['eventid']
		self.event = get_object_or_404(TrainingEvents, pk=event_id)
		main_query = Participant.objects.filter(event_id=event_id)

		if self.event.training_status == 2:
			return EventAttendance.objects.filter(event_id=event_id).select_related(
				'participant', 'participant__college', 'participant__state'
			)
		elif self.event.training_status == 1:
			return main_query.filter(reg_approval_status=1).select_related('college', 'state')
		else:
			return main_query.filter(Q(payment_status__status=1)| Q(registartion_type__in=(1,3)))

	def get_context_data(self, **kwargs):
		context = super(EventParticipantsListView, self).get_context_data(**kwargs)
		context['event'] = self.event
		context['eventid'] = self.event.id
		context['is_event_closed'] = self.event.training_status == 2
		return context


@csrf_exempt
def ajax_add_teststatus(request):
	partid = int(request.POST.get("partid"))
	mdlcourseid = int(request.POST.get("mdlcourseid"))
	mdlquizid = int(request.POST.get("mdlquizid"))
	fossid = int(request.POST.get("fossid"))
	eventid = int(request.POST.get("eventid"))
	fossId = FossCategory.objects.get(id=fossid)

	useremail = request.user.email

	testentry = EventTestStatus()
	testentry.participant_id= partid	
	testentry.event_id = eventid
	testentry.mdlemail = useremail
	testentry.fossid = fossId
	testentry.mdlcourse_id = mdlcourseid
	testentry.mdlquiz_id = mdlquizid
	testentry.mdlattempt_id = 0

	hasPrevEntry = EventTestStatus.objects.filter(participant_id=partid, event_id=eventid, mdlemail=useremail, fossid=fossId, mdlcourse_id=mdlcourseid, mdlquiz_id=mdlquizid, part_status__lt=2).first()

	check = False
	if not hasPrevEntry:
		try:
			testentry.save()
			check = True
		except:
			check = False
	else:
		check = True

	return HttpResponse(json.dumps(check), content_type='application/json')


class ILWTestCertificate(object):
  def custom_strftime(self, format, t):
    return t.strftime(format).replace('{S}', str(t.day) + self.suffix(t.day))

  def suffix(self, d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

  def create_ilwtest_certificate(self, event, user, teststatus):
    training_start = event.event_start_date
    training_end = event.event_end_date
    event_type = event.event_type
    participantname = f"{user.first_name} {user.last_name}"
    response = HttpResponse(content_type='application/pdf')
    if event_type == "HN":
        filename = (participantname+'-'+event.course.name+"-Participant-Test-Certificate").replace(" ", "-")
    else:
        filename = (participantname+'-'+teststatus.fossid.foss+"-Participant-Test-Certificate").replace(" ", "-")

    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = BytesIO ()
    imgDoc = canvas.Canvas(imgTemp)

    # Title
    imgDoc.setFont('Helvetica', 25, leading=None)
    if event.event_type != "INTERN":
        imgDoc.drawCentredString(405, 470, "Certificate for Completion of Training")
        # Draw image on Canvas and save PDF in buffer
        imgPath = get_signature(training_start)
        imgDoc.drawImage(imgPath, 600, 100, 150, 76)

    #password
    certificate_pass = ''

    if teststatus.cert_code:
        certificate_pass = teststatus.cert_code
        teststatus.part_status = 3 #certificate downloaded test over
        teststatus.save()
    else:
        certificate_pass = str(teststatus.participant_id)+id_generator(10-len(str(teststatus.participant_id)))
        teststatus.cert_code = certificate_pass
        teststatus.part_status = 3 #certificate downloaded test over
        teststatus.save()

    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)

    if event_type != "HN":
        credits = "<p><b>Credits:</b> "+str(teststatus.fossid.credits)+"&nbsp&nbsp&nbsp<b>Score:</b> "+str('{:.2f}'.format(teststatus.mdlgrade))+"%</p>"

    #paragraphe
    text = get_test_certi_text(event, user, teststatus)
    centered = ParagraphStyle(name = 'centered',
      fontSize = 16,
      leading = 30,
      alignment = 0,
      spaceAfter = 20
    )
    imgDoc.setFillColorRGB(0, 0, 0)
    imgDoc.drawCentredString(150, 115, training_end.strftime('%d %B %Y'))
	
    p = Paragraph(text, centered)
    p.wrap(650, 200)
    p.drawOn(imgDoc, 4.2 * cm, 5.5 * cm)
    imgDoc.save()
    # Use PyPDF to merge the image-PDF into the template
    template_path = get_ilw_certificate(event, 'test')
    page = PdfFileReader(open(template_path,"rb")).getPage(0)
    overlay = PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)

    #Save the result
    output = PdfFileWriter()
    output.addPage(page)

    #stream to browser
    outputStream = response
    output.write(response)
    outputStream.close()

    return response


class EventTestCertificateView(ILWTestCertificate, View):
  template_name = ""
  
  def dispatch(self, *args, **kwargs):
    return super(EventTestCertificateView, self).dispatch(*args, **kwargs)

  def post(self, request, *args, **kwargs):
    eventid = self.request.POST.get("eventid")
    event = TrainingEvents.objects.get(id=eventid)
    if event.event_type == "HN":
        teststatus = EventTestStatus.objects.filter(event_id=eventid, participant__user=self.request.user, mdlemail=self.request.user.email, mdlgrade__gte=settings.PASS_GRADE).order_by('-mdlgrade').first()
    else:
        teststatus = EventTestStatus.objects.filter(event_id=eventid, fossid=kwargs['testfossid'], mdlemail=self.request.user.email, mdlgrade__gte=settings.PASS_GRADE).order_by('-mdlgrade').first()
    if event:
      return self.create_ilwtest_certificate(event, self.request.user, teststatus)
    else:
      messages.error(self.request, "Permission Denied!")
    return HttpResponseRedirect("/")


def ilwtestkey_verification(serial):
    context = {}
    try:
        certificate = EventTestStatus.objects.get(cert_code=serial)
        name = certificate.participant.name
        foss = certificate.fossid.foss
        detail = {}
        detail['Participant_Name'] = name
        detail['Foss'] = foss
        detail['Event Details'] = certificate.event
        detail['Event Date'] = str(certificate.event.event_start_date)+" to "+str(certificate.event.event_end_date)
        detail['Event Host College'] = certificate.event.host_college
        # detail['Test_Date'] = tdate

        context['certificate'] = certificate
        context['detail'] = detail
        context['serial_no'] = True
    except EventTestStatus.DoesNotExist:
        context["invalidserial"] = 1
    return context

@csrf_exempt
def verify_ilwtest_certificate(request):
    context = {}
    ci = RequestContext(request)
    if request.method == 'POST':
        serial_no = request.POST.get('serial_no').strip()
        context = ilwtestkey_verification(serial_no)
        return render(request, 'verify_ilwtest_certificate.html', context)
    return render(request, 'verify_ilwtest_certificate.html', {})

@login_required
def add_company(request):
	"""create new company"""
	user = request.user
	if not (is_event_manager(user) or is_resource_person(user)):
		raise PermissionDenied()
	
	if request.method == 'POST':
		form = CompanyForm(request.POST)
		if form.is_valid():
			form_data = form.save(commit=False)
			form_data.added_by = user
			form_data.save()
			messages.success(request, form_data.name+" has been updated")
			return HttpResponseRedirect("/training/companies/new/")
	else:
		context = {}
		#pass form
		context['form'] = CompanyForm()
		return render(request, 'company_form.html', context)
	
@login_required
def list_companies(request):
	user = request.user
	if not (is_event_manager(user) or is_resource_person(user)):
		raise PermissionDenied()
	
	context = {}
	header = {
		1: SortableHeader('#', False),
		2: SortableHeader('Name', True),
		3: SortableHeader('Type', True),
		4: SortableHeader('State', True),
		5: SortableHeader('District', True),
		6: SortableHeader('Added By', True),
		7: SortableHeader('Action', False),
	}

	collectionSet = Company.objects.select_related('added_by').all()
	raw_get_data = request.GET.get('o', None)
	collection = get_sorted_list(request, collectionSet, header, raw_get_data)
	ordering = get_field_index(raw_get_data)
	collection = CompanyFilter(request.GET, queryset=collection)
	context['form'] = collection.form
	page = request.GET.get('page')
	collection = get_page(collection.qs, page)
	
	context['collection'] = collection
	context['header'] = header
	context['ordering'] = ordering

	return render(request, 'companies.html', context)

@login_required
def edit_company(request, rid = None):
	user = request.user
	if not (is_event_manager(user) or is_resource_person(user)):
		raise PermissionDenied()

	if request.method == 'POST':
		company = Company.objects.get(id=rid)
		form = CompanyForm(request.POST, instance=company)
		if form.is_valid():
			form.save()
			messages.success(request, "Company details has been updated")
			return HttpResponseRedirect("/training/edit_company/"+str(rid)+"/")
		context = { 'form': form }
		return HttpResponseRedirect("/training/companies/new/")
	else:
		try:
			company = Company.objects.get(id=rid)
			context = {}
			context['form'] = CompanyForm(instance=company)
			context['edit'] = rid
			return render(request, 'company_form.html', context)
		except:
			raise PermissionDenied()


@csrf_exempt
def proxy_health_api(request):
    url = HN_API
    params = {
        "courseName": request.GET.get("courseName"),
        "catIds": request.GET.get("catIds"),
        "lanIds": request.GET.get("lanIds"),
    }
    resp = requests.get(url, params=params)
    try:
        return JsonResponse(resp.json())
    except Exception as e:
        return JsonResponse({"error": "Invalid response from remote API"}, status=500)