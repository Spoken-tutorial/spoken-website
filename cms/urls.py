from django.conf.urls import patterns, url, include
from cms import views
urlpatterns = patterns('',

	url(r'accounts/register/', views.account_register, name='register'),
	url(r'accounts/login/', views.account_login, name='login'),
	url(r'accounts/logout/', views.account_logout, name='logout'),
	url(r'accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>\w+)$', views.confirm, name='confirm'),
	url(r'accounts/profile/(?P<username>\w+)/$', views.account_profile, name='profile'),
	url(r'(?P<permalink>.+)/$', 'cms.views.dispatcher', name="dispatcher"),
)
