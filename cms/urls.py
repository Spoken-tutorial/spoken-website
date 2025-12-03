# Third Party Stuff
from django.conf.urls import include, url
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
	url(r'^accounts/register/$',  account_register, name='register'),
	url(r'^accounts/login/$',  account_login, name='login'),
	url(r'^accounts/logout/$',  account_logout, name='logout'),
	url(r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$",  confirm, name='confirm'),
	url(r"^accounts/forgot-password/$",  password_reset, name='password_reset'),
	url(r"^accounts/change-password/$",  change_password, name='change_password'),
	url(r"^accounts/profile/(?P<username>[\w. @-]+)/$",  account_profile, name='profile'),
	url(r"^accounts/view-profile/(?P<username>[\w. @-]+)/$",  account_view_profile, name='view_profile'),
	url(r'^accounts/verify/$',  verify_email, name='verify_email'),
	url(r'^accounts/confirm_student/(?P<token>\w+)/$',  confirm_student, name='confirm_student'),
	url(r'^purchase',  purchase, name='purchase'),
	

	#sitemaps
    url(r'^sitemap\.xml/$', sitemap, {'sitemaps' : spoken_sitemaps } , name='spoken_sitemap'),
	
	url(r'^(?P<permalink>.+)/$',  dispatcher, name="dispatcher"),
    

]