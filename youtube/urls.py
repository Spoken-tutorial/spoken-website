from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Main pages dispatcher
    url(r'^$', 'youtube.views.home', name="home"),
    url(r'^cron/foss-playlist/$', 'youtube.views.cron_foss_playlist', name="cron_foss_playlist"),
    url(r'^cron/add-video/$', 'youtube.views.cron_add_video', name="cron_add_video"),
    url(r'^test-list-videos/$', 'youtube.views.test_list_videos', name="test_list_videos"),
    url(r'^oauth2callback/(\w+)/$', 'youtube.views.auth_return', name="auth_return"),
)
