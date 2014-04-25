from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^login/', 'mdldjango.views.mdl_login', name='mdl_login'),
	url(r'^logout/', 'mdldjango.views.mdl_logout', name='mdl_logout'),
	url(r'^index/', 'mdldjango.views.index', name='mdl_index'),
	url(r'^offline-data/', 'mdldjango.views.offline_details', name='mdl_offline_workshop_details'),
)
