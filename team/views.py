from django.shortcuts import render

# Create your views here.
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import Group, User
from cms.models import *
from django.conf import settings

class TeamListView(ListView):
  queryset = None
  paginate_by = 100
 
  def dispatch(self, *args, **kwargs):
    print kwargs['role']
    self.queryset = User.objects.filter(groups__name=kwargs['role']).order_by('first_name')
    return super(TeamListView, self).dispatch(*args, **kwargs)
