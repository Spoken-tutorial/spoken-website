# Third Party Stuff
from django.urls import re_path
from cms.views import *
# Spoken Tutorial Stuff
from mdldjango.urls import *
from django.contrib.sitemaps.views import sitemap
from spoken.sitemaps import SpokenStaticViewSitemap
from donate.views import *

app_name = 'cms'

spoken_sitemaps = {
    'static': SpokenStaticViewSitemap,
}

urlpatterns = [
	re_path(r'^accounts/register/$',  account_register, name='register'),
	re_path(r'^accounts/login/$',  account_login, name='login'),
	re_path(r'^accounts/logout/$',  account_logout, name='logout'),
	re_path(r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$",  confirm, name='confirm'),
	re_path(r"^accounts/forgot-password/$",  password_reset, name='password_reset'),
	re_path(r"^accounts/change-password/$",  change_password, name='change_password'),
	re_path(r"^accounts/profile/(?P<username>[\w. @-]+)/$",  account_profile, name='profile'),
	re_path(r"^accounts/view-profile/(?P<username>[\w. @-]+)/$",  account_view_profile, name='view_profile'),
	re_path(r'^accounts/verify/$',  verify_email, name='verify_email'),
	re_path(r'^accounts/confirm_student/(?P<token>\w+)/$',  confirm_student, name='confirm_student'),
	re_path(r'^purchase',  purchase, name='purchase'),
	

	#sitemaps
    re_path(r'^sitemap\.xml/$', sitemap, {'sitemaps' : spoken_sitemaps } , name='spoken_sitemap'),
	
	re_path(r'^(?P<permalink>.+)/$',  dispatcher, name="dispatcher"),


]