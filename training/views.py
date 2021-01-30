# Django imports
from django.shortcuts import render, redirect
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers import serialize
from django.db.models import Q
from django.contrib.auth.models import User
from django.urls import reverse
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
from creation.models import TutorialResource, Language
from events.decorators import group_required
from events.models import *
from events.views import is_resource_person, is_administrator, get_page 
from events.filters import ViewEventFilter, PaymentTransFilter, TrEventFilter
from cms.sortable import *
from cms.views import create_profile, send_registration_confirmation
from cms.models import Profile
from certificate.views import _clean_certificate_certificate
from django.http import HttpResponse
import os, sys
from string import Template
import subprocess

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



today = date.today()

class TrainingEventCreateView(CreateView):
	form_class = CreateTrainingEventForm
	model = TrainingEvents
	template_name = "create_event.html"
	success_url = "/software-training/"

	@method_decorator(group_required("Resource Person"))
	def get(self, request, *args, **kwargs):
		return render(self.request, self.template_name, {'form': self.form_class()})

	def form_valid(self, form, **kwargs):
		self.object = form.save(commit=False)
		self.object.entry_user = self.request.user
		self.object.Language_of_workshop = Language.objects.get(id=22)
		self.object.save()

		messages.success(self.request, "New Event created successfully.")
		return HttpResponseRedirect(self.success_url)

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
			self.events = TrainingEvents.objects.filter(event_end_date__lt=today)
		if self.status == 'ongoing':
			self.events = TrainingEvents.objects.filter(event_end_date__gte=today)
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
		if self.request.user:
			context['user'] = self.request.user
		return context

@csrf_exempt
def register_user(request):
	form = RegisterUser()
	template_name = "register_user.html"
	context = {}
	context['form']= form
	
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
	if request.method == 'POST':
		event_id = request.POST.get("event_id_info")
		if event_id:
			event_register = TrainingEvents.objects.get(id=event_id)
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
		event = TrainingEvents.objects.get(id=event_obj)
		form = RegisterUser(request.POST)
		if form.is_valid():
			form_data = form.save(commit=False)
			form_data.user = request.user
			form_data.event = event
			try:
				form_data.college = AcademicCenter.objects.get(institution_name=request.POST.get('college'))
			except:
				form_data.college = AcademicCenter.objects.get(id=request.POST.get('dropdown_college'))	
			user_data = is_user_paid(request.user, form_data.college.id)
			if user_data[0]:
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
				context = {'participant_obj':form_data}
				return render(request, template_name, context)
			else:
				return form_data
		else:
			messages.warning(request, 'Invalid form payment request.')
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


class EventUpdateView(UpdateView):
	model = TrainingEvents
	form_class = CreateTrainingEventForm
	success_url = "/training/event/rp/ongoing/"


#used to display evnets to mngrs under dashboard link
def listevents(request, role, status):
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
		pcount, mcount, fcount = get_all_events_detail(queryset, event_type) if event_type else get_all_events_detail(queryset)
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
	context['today'] = today
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
		for i, row in enumerate(rows_data):
			user = self.get_create_user(row)
			
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
			user.save()
			create_profile(user, row[8].strip())
			send_registration_confirmation(user)
			return user


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

		self.queryset =	main_query.filter(Q(payment_status__status=1)| Q(registartion_type__in=(1,3)))
		self.unsuccessful_payee = main_query.filter(payment_status__status__in=(0,2))

		
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
	user_details = is_user_paid(request.user, int(college_id))
	check = False
	if user_details[0]:
			check = True
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

  def create_fdptraining_certificate(self, event, participantname):
    training_start = event.event_start_date
    training_end = event.event_end_date
    event_type = event.event_type
    response = HttpResponse(content_type='application/pdf')
    filename = (participantname+'-'+event.foss.foss+"-Participant-Certificate").replace(" ", "-");

    response['Content-Disposition'] = 'attachment; filename='+filename+'.pdf'
    imgTemp = BytesIO ()
    imgDoc = canvas.Canvas(imgTemp)

    # Title
    imgDoc.setFont('Helvetica', 35, leading=None)
    imgDoc.drawCentredString(405, 470, "Certificate of Participation")

    #password
    certificate_pass = ''
    imgDoc.setFillColorRGB(211, 211, 211)
    imgDoc.setFont('Helvetica', 10, leading=None)
    imgDoc.drawString(10, 6, certificate_pass)

    # Draw image on Canvas and save PDF in buffer
    imgPath = settings.MEDIA_ROOT +"sign.jpg"
    imgDoc.drawImage(imgPath, 600, 100, 150, 76)

    #paragraphe
    text = "This is to certify that <b>"+participantname +"</b> has participated in \
    <b>"+event.get_event_type_display()+"</b> from <b>"\
    + str(training_start) +"</b> to <b>"+ str(training_end) +\
    "</b> on <b>"+event.foss.foss+"</b> organized by <b>"+\
    event.host_college.institution_name+\
    "</b> with  course material provided by Spoken Tutorial Project, IIT Bombay.\
    <br /><br /> This training is offered by the Spoken Tutorial Project, IIT Bombay."

    centered = ParagraphStyle(name = 'centered',
      fontSize = 16,
      leading = 30,
      alignment = 0,
      spaceAfter = 20
    )

    p = Paragraph(text, centered)
    p.wrap(650, 200)
    p.drawOn(imgDoc, 4.2 * cm, 7 * cm)
    imgDoc.save()
    # Use PyPDF to merge the image-PDF into the template
    if event_type == "FDP":
        page = PdfFileReader(open(settings.MEDIA_ROOT +"fdptr-certificate.pdf","rb")).getPage(0)
    else:
        page = PdfFileReader(open(settings.MEDIA_ROOT +"tr-certificate.pdf","rb")).getPage(0)
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
    print(eventid)
    event = TrainingEvents.objects.get(id=eventid)
    participantname = self.request.user.first_name+" "+self.request.user.last_name    

    if event:
      return self.create_fdptraining_certificate(event, participantname)
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

	state = State.objects.filter(id__in=rp_states.values('state')).values('name')

	
	context = {}

	if request.method == 'GET':
		form = TrainingManagerPaymentForm(user,request.GET)

		allpaydetails = get_transaction_details(request, purpose)	
		request_type = request.GET.get('request_type')
		if request_type == 'R':
		  context['total'] = allpaydetails.aggregate(Sum('amount'))

	# else:
	# 	form = TrainingManagerPaymentForm(user=request.user)
	context['form'] = form
	context['user'] = user
	context['transactiondetails'] = allpaydetails
	context['purpose'] = purpose
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
	            event.event_name+','+event.foss.foss,
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
	queryset = ""
	unsuccessful_payee = ""
	paginate_by = 500
	success_url = ""

	def dispatch(self, *args, **kwargs):
		self.event = TrainingEvents.objects.get(pk=kwargs['eventid'])
		main_query = Participant.objects.filter(event_id=kwargs['eventid'])

		self.queryset =	main_query.filter(Q(payment_status__status=1)| Q(registartion_type__in=(1,3)))
		# self.unsuccessful_payee = main_query.filter(payment_status__status__in=(0,2))

		
		if self.event.training_status == 1:
			self.queryset = main_query.filter(reg_approval_status=1)

		if self.event.training_status == 2:
			self.queryset = self.event.eventattendance_set.all()
		return super(EventParticipantsListView, self).dispatch(*args, **kwargs)


	def get_context_data(self, **kwargs):
		context = super(EventParticipantsListView, self).get_context_data(**kwargs)
		
		context['event'] = self.event
		context['eventid'] = self.event.id
		return context