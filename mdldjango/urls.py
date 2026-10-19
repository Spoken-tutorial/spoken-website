# Third Party Stuff
from django.conf.urls import url
from django.contrib import admin
from mdldjango.views import *
from django.shortcuts import redirect
from spoken.config import EDUPYRAMIDS_URL

app_name = 'mdldjango'
admin.autodiscover()

urlpatterns = [
    # url(r'^login/$', mdl_login, name='mdl_login'),
    url( r'^login/$',lambda request: redirect(EDUPYRAMIDS_URL + '/particpant/login/'),name='mdl_login'),
    url(r'^forgot-password/$', forget_password, name='forgot_password'),
    url(r'^feedback/(\d+)/$', feedback, name='feedback'),
    # url(r'^register/$', mdl_register, name='mdl_register'),
    url(r'^register/$',lambda request: redirect(EDUPYRAMIDS_URL + '/Participant/register/'),name='mdl_register'),   
    url(r'^logout/$', mdl_logout, name='mdl_logout'),
    url(r'^index/$', index, name='mdl_index'),
    url(r'^offline-data/(\d+)/(\d+)/$', offline_details, name='mdl_offline_workshop_details'),
]
