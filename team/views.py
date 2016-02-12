from django.shortcuts import render

# Create your views here.
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import Group, User
from cms.models import *
from django.conf import settings

class TeamContributorListView(ListView):
  queryset = None
  paginate_by = 100
 
  def dispatch(self, *args, **kwargs):
    self.queryset = User.objects.filter(groups__name='Contributor').order_by('first_name')
    #self.queryset = Profile.objects.filter(user_id__in = User.objects.filter(groups__name='Contributor') ).order_by('user_id')
    return super(TeamContributorListView, self).dispatch(*args, **kwargs)
  
  """def get_context_data(self, **kwargs):
    context = super(TeamContributorListView, self).get_context_data(**kwargs)
    users = User.objects.filter(groups__name='Contributor').order_by('first_name')
    #for member in users:
    #  profile = Profile.objects.filter(user_id=member.id)
    #  context['profile'] = profile
    #  context['media_url'] = settings.MEDIA_URL
    #  context['temp'] = 'hello'
    return context"""
  
  
  
class TeamDomainListView(ListView):
  queryset = None
  paginate_by = 100
 
  def dispatch(self, *args, **kwargs):
    self.queryset = User.objects.filter(groups__name='Domain-Reviewer').order_by('first_name')
    return super(TeamDomainListView, self).dispatch(*args, **kwargs)
    
class TeamQualityReviewerListView(ListView):
  queryset = None
  paginate_by = 100
 
  def dispatch(self, *args, **kwargs):
    self.queryset = User.objects.filter(groups__name='Quality-Reviewer').order_by('first_name')
    return super(TeamQualityReviewerListView, self).dispatch(*args, **kwargs)
    
class TeamExternalContributorListView(ListView):
  queryset = None
  paginate_by = 100
 
  def dispatch(self, *args, **kwargs):
    self.queryset = User.objects.filter(groups__name='External-Contributor').order_by('first_name')
    return super(TeamExternalContributorListView, self).dispatch(*args, **kwargs)
