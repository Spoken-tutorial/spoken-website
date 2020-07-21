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
	if request.method == 'POST':
		form = RegisterUser(request.POST)
		form_data = form.save(commit=False)
		form_data.user = request.user
		form_data.college = AcademicCenter.objects.get(id=request.POST.get('college'))
		form_data.save()
	return render(request, template_name,context)
