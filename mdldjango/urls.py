from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	url(r'^login/', 'mdldjango.views.mdl_login', name='mdl_login'),
	url(r'^register/', 'mdldjango.views.mdl_register', name='mdl_register'),
	url(r'^logout/', 'mdldjango.views.mdl_logout', name='mdl_logout'),
	url(r'^index/$', 'mdldjango.views.index', name='mdl_index'),
	url(r'^offline-data/(\d+)/(\d+)/$', 'mdldjango.views.offline_details', name='mdl_offline_workshop_details'),
)
