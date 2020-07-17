from django.shortcuts import render
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from training.models import *
from training.forms import *
from django.utils.decorators import method_decorator
from events.decorators import group_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .helpers import is_user_paid
from .forms import *
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


class RegisterUserView(CreateView):
	"""docstring for RegisterUserView"""
	form_class = RegisterUser
	template_name = "register_user.html"
	context = {}
	context['user_paid_college'] = is_user_paid(self.request)
	return render(self.request, template_name, context)
	def __init__(self, arg):
		super(RegisterUserView, self).__init__()
		self.arg = arg
		

