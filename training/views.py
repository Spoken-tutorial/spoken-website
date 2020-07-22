from django.shortcuts import render
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from .models import *
from .forms import *
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from events.models import State
from events.decorators import group_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.core.serializers import serialize
from .helpers import is_user_paid
import json
from datetime import datetime,date
# Create your views here.
class TrainingEventCreateView(CreateView):
	form_class = CreateTrainingEventForm
	model = TrainingEvents
	template_name = "create_event.html"
	success_url = "/"

	@method_decorator(group_required("Organiser"))
	def get(self, request, *args, **kwargs):
		return render(self.request, self.template_name, {'form': self.form_class()})

	def form_valid(self, form, **kwargs):
		self.object = form.save(commit=False)
		self.object.entry_user = self.request.user
		self.object.save()

		messages.success(self.request, "New Event created successfully.")
		return HttpResponseRedirect(self.success_url)


class TrainingEventsListView(ListView):
	model = TrainingEvents
	paginate_by = 50  # if pagination is desired

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
			self.events = TrainingEvents.objects.filter(id__in=Participant.objects.filter(user_id=self.request.user.id).values('event_id'))
		return super(TrainingEventsListView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(TrainingEventsListView, self).get_context_data(**kwargs)

		context['status'] =  self.status
		context['events'] =  self.events
		context['show_myevents'] = self.show_myevents
		if self.request.user:
			context['userid'] = self.request.user.id
		return context

@csrf_exempt
def register_user(request):
	form = RegisterUser()
	template_name = "register_user.html"
	context = {}
	context['form']= form
	if request.method == 'POST':
		form = RegisterUser(request.POST)
		form_data = form.save(commit=False)
		form_data.user = request.user
		form_data.college = AcademicCenter.objects.get(id=request.POST.get('college'))
		form_data.save()
	return render(request, template_name,context)
