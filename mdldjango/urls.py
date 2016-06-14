from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$', views.mdl_login, name='mdl_login'),
    url(r'^forgot-password/$', views.forget_password, name='forgot_password'),
    url(r'^feedback/(\d+)/$', views.feedback, name='feedback'),
    url(r'^register/$', views.mdl_register, name='mdl_register'),
    url(r'^logout/$', views.mdl_logout, name='mdl_logout'),
    url(r'^index/$', views.index, name='mdl_index'),
    url(r'^offline-data/(\d+)/(\d+)/$', views.offline_details, name='mdl_offline_workshop_details'),
]
