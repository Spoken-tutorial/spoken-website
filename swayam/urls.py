from django.conf.urls import url

from . import views


app_name = 'swayam'


urlpatterns = [

    url(
        r'^sso/start/$',
        views.sso_start,
        name='sso-start',
    ),

    url(
        r'^sso/callback/$',
        views.sso_callback,
        name='sso-callback',
    ),

    url(
        r'^save-progress/$',
        views.save_progress,
        name='save-progress',
    ),
    url(
        r'^page-views/$',
        views.swayam_page_views,
        name='swayam_page_views',
    ),
    url(
        r'^sso/login/$',
        views.sso_login,
        name='sso-login',
    ),
]