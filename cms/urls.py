from mdldjango.urls import *
from django.conf.urls import patterns, url, include
urlpatterns = patterns('',

	url(r'^accounts/register/$', 'cms.views.account_register', name='register'),
	url(r'^accounts/login/$', 'cms.views.account_login', name='login'),
	url(r'^accounts/logout/$', 'cms.views.account_logout', name='logout'),
	url(r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$", 'cms.views.confirm', name='confirm'),
	url(r"^accounts/forgot-password/$", 'cms.views.password_reset', name='password_reset'),
	url(r"^accounts/change-password/$", 'cms.views.change_password', name='change_password'),
	url(r"^accounts/profile/(?P<username>[\w. @-]+)/$", 'cms.views.account_profile', name='profile'),
	url(r"^accounts/view-profile/(?P<username>[\w. @-]+)/$", 'cms.views.account_view_profile', name='view_profile'),
	url(r'^accounts/verify/$', 'cms.views.verify_email', name='verify_email'),
	url(r'^accounts/confirm_student/(?P<token>\w+)/$', 'cms.views.confirm_student', name='confirm_student'),
	url(r'^(?P<permalink>.+)/$', 'cms.views.dispatcher', name="dispatcher"),
)
