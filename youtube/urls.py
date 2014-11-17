from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Main pages dispatcher
    url(r'^$', 'youtube.views.home', name="home"),
    url(r'^delete-videos/$', 'youtube.views.delete_all_videos', name="delete_all_videos"),
    url(r'^oauth2callback/(\w+)/$', 'youtube.views.auth_return', name="auth_return"),
)
