from django.shortcuts import render

# Create your views here.
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import Group, User

class TeamContributorListView(ListView):
  queryset = None
  paginate_by = 1000
 
  def dispatch(self, *args, **kwargs):
    self.queryset = User.objects.filter(groups__name='Contributor')
    return super(TeamContributorListView, self).dispatch(*args, **kwargs)
