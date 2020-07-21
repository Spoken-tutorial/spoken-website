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
from .helpers import is_user_paid, user_college
import json
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
				user_data = is_user_paid(request)
				if user_data[0]:
					print("college",user_data[1])
					form.fields["college"].initial = user_data[1]
				else:
					print("user_college(request)",user_college(request))
					form.fields["college"].initial = user_college(request)
			except Exception as e:
				raise e

	if request.method == 'POST':
		event_id = request.POST.get("event_id_info")
		if event_id:
			event_register = TrainingEvents.objects.get(id=event_id)
			form.fields["event"].initial = event_register
			form.fields['event'].widget.attrs['readonly'] = True
		else:
			form = RegisterUser(request.POST)
			form_data = form.save(commit=False)
			form_data.user = request.user
			form_data.college = AcademicCenter.objects.get(id=request.POST.get('college'))
			form_data.save()
	return render(request, template_name,context)
