from django.shortcuts import render
from django.db.models import Q

# Create your views here.
from django.views.generic import View, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import Group, User
from cms.models import *
from django.conf import settings

class TeamListView(ListView):
  queryset = None
  paginate_by = 21
 
  def dispatch(self, *args, **kwargs):
    self.type = kwargs['role']
    print self.type
    if self.type == 'Creation-Team':
      #self.queryset = User.objects.filter(Q(groups__name='Contributor') | Q(groups__name='Domain-Reviewers') | Q(groups__name='Quality-Reviewers')).order_by('first_name')
      self.queryset = User.objects.filter(groups__name__in=['Contributor' , 'Domain-Reviewers' , 'Quality-Reviewers']).order_by('first_name')
      #for user in self.queryset:
        #self.category=Group.objects.filter(user__id=user.id)
        #print self.category
    else:
      self.queryset = User.objects.filter(groups__name=kwargs['role']).order_by('first_name')
    return super(TeamListView, self).dispatch(*args, **kwargs)
    
  def get_context_data(self, **kwargs):
    context = super(TeamListView, self).get_context_data(**kwargs)
    context['role'] = self.type
    return context
