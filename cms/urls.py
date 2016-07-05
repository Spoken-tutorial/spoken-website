from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^accounts/register/$', views.account_register, name='register'),
    url(r'^accounts/login/$', views.account_login, name='login'),
    url(r'^accounts/logout/$', views.account_logout, name='logout'),
    url(r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$", views.confirm, name='confirm'),
    url(r"^accounts/forgot-password/$", views.password_reset, name='password_reset'),
    url(r"^accounts/change-password/$", views.change_password, name='change_password'),
    url(r"^accounts/profile/(?P<username>[\w. @-]+)/$", views.account_profile, name='profile'),
    url(r"^accounts/view-profile/(?P<username>[\w. @-]+)/$", views.account_view_profile, name='view_profile'),
    url(r'^(?P<permalink>.+)/$', views.dispatcher, name="dispatcher"),
]
