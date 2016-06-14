from django.conf.urls import url

urlpatterns = [
    url(r'^accounts/register/$', 'cms.views.account_register', name='register'),
    url(r'^accounts/login/$', 'cms.views.account_login', name='login'),
    url(r'^accounts/logout/$', 'cms.views.account_logout', name='logout'),
    url(r"^accounts/confirm/(?P<confirmation_code>\w+)/(?P<username>[\w. @-]+)/$", 'cms.views.confirm', name='confirm'),
    url(r"^accounts/forgot-password/$", 'cms.views.password_reset', name='password_reset'),
    url(r"^accounts/change-password/$", 'cms.views.change_password', name='change_password'),
    url(r"^accounts/profile/(?P<username>[\w. @-]+)/$", 'cms.views.account_profile', name='profile'),
    url(r"^accounts/view-profile/(?P<username>[\w. @-]+)/$", 'cms.views.account_view_profile', name='view_profile'),
    url(r'^(?P<permalink>.+)/$', 'cms.views.dispatcher', name="dispatcher"),
]
