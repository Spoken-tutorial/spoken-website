from django.shortcuts import render
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from .models import *
from .forms import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from events.models import State
from creation.models import TutorialResource, Language
from events.decorators import group_required
from events.views import is_resource_person, is_administrator
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers import serialize
from .helpers import is_user_paid, user_college, EVENT_AMOUNT, handle_uploaded_file
import json
from datetime import datetime,date
from  events.filters import ViewEventFilter
from cms.sortable import *
from events.views import get_page


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


class TrainingEventsListView(ListView):
	model = TrainingEvents

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
			participant = Participant.objects.filter(user_id=self.request.user.id)
			self.events = participant
		return super(TrainingEventsListView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(TrainingEventsListView, self).get_context_data(**kwargs)

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
		form.fields["name"].initial = user.get_full_name()
		form.fields["email"].initial = getattr(user, 'email')
		form.fields['email'].widget.attrs['readonly'] = True
		if user.profile_set.all():
			try:
				form.fields["state"].initial = getattr(user.profile_set.all()[0], 'state')
				user_data = is_user_paid(request.user)
				if user_data[0]:
					college = user_data[1]
				else:
					college = user_college(request)
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
			form.fields["foss_language"].queryset = langs
			form.fields["amount"].initial = EVENT_AMOUNT[event_register.event_type]
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
			user_data = is_user_paid(request.user)
			if event.host_college == form_data.college:
				print("host")
				form_data.registartion_type = 0 #host College
			elif user_data[0]:
				print("Subscribed")
				form_data.registartion_type = 1 #Subscribed College
			else:
				form_data.registartion_type = 2 #Manual reg- paid 500

			form_data.save()
			event_name = event.event_name
			if user_type == 'paid':
				context = {'name':name, 'email':email, 'event':event_name}
				return render(request, template_name,context)
			else:
				return form_data
		else:
			messages.warning(request, 'Invalid form payment request.')
			return redirect('training:list_events' 'ongoing' )


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

def listevents(request, role, status):
	context = {}
	user = request.user
	if not (user.is_authenticated() and (is_resource_person(user) or is_administrator(user))):
		raise PermissionDenied()

	if (not role ) or (not status):
		raise PermissionDenied()


	status_list = {'ongoing': 0, 'completed': 1, 'closed': 2,}
	roles = ['rp', 'em']
	if role in roles and status in status_list:
		if status == 'ongoing':
			queryset = TrainingEvents.objects.filter(training_status__lte=1, event_end_date__gte=today)
		elif status == 'completed':
			queryset = TrainingEvents.objects.filter(training_status=1, event_end_date__lt=today)
		elif status == 'closed':
			queryset = TrainingEvents.objects.filter(training_status=2)

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
		  'event_start_date',
		  True,
		  'Event Start Date'
		),
		8: SortableHeader(
		  'event_end_date',
		  True,
		  'Event End Date'
		),
		9: SortableHeader('Action', False)
		}

		raw_get_data = request.GET.get('o', None)
		queryset = get_sorted_list(
			request,
			queryset,
			header,
			raw_get_data
		)
		collection= ViewEventFilter(request.GET, queryset=queryset, user=user)
      

	else:
		raise PermissionDenied()

	context['form'] = collection.form
	page = request.GET.get('page')
	collection = get_page(collection.qs, page)
	context['collection'] =  collection
	context['role'] = role
	context['status'] = status
	context['header'] = header
	context['ordering'] = get_field_index(raw_get_data)

	return render(request,'event_status_list.html',context)


def close_event(request, pk):
	context = {}
	user = request.user
	if not (user.is_authenticated() and is_resource_person(user)):
		raise PermissionDenied()
	
	event = TrainingEvents.objects.get(id=pk)
	if event:
		event.training_status = 2 #rclose event
		event.save()
		messages.success(request, 'Event has been closed successfully')
	else:
		print("Error")
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
		print("Error")
		messages.error(request, 'Request not sent.Please try again.')
	return HttpResponseRedirect("/training/event/rp/ongoing/")


class ParticipantCreateView(CreateView):
	form_class = UploadParticipantsForm
	success_url = '/'

	@method_decorator(group_required("Resource Person"))
	def dispatch(self, *args, **kwargs):
		if 'eventid' in kwargs:
			try:
				self.event = TrainingEvents.objects.filter(pk=kwargs['eventid'])
			except:
				print("Error")
				messages.error(request, 'Event not found')
		return super(ParticipantCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(ParticipantCreateView, self).get_context_data(**kwargs)
		context['event']= self.event
		return context

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			print(handle_uploaded_file(f))
			return redirect(self.success_url)
		else:
			return render(request, self.template_name, {'form': form})

