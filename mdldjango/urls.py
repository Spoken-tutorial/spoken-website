# Third Party Stuff
from django.urls import re_path, path
from django.contrib import admin
from mdldjango.views import *
app_name = 'mdldjango'
admin.autodiscover()

urlpatterns = [
    re_path(r'^login/$', mdl_login, name='mdl_login'),
    re_path(r'^forgot-password/$', forget_password, name='forgot_password'),
    re_path(r'^feedback/(\d+)/$', feedback, name='feedback'),
    re_path(r'^register/$', mdl_register, name='mdl_register'),
    re_path(r'^logout/$', mdl_logout, name='mdl_logout'),
    re_path(r'^index/$', index, name='mdl_index'),
    re_path(r'^offline-data/(\d+)/(\d+)/$', offline_details, name='mdl_offline_workshop_details'),
]
