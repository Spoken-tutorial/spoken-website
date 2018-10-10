# Third Party Stuff
from django.conf.urls import url
from youtube.views import *
app_name = 'youtube'
urlpatterns = [ # noqa
    url(r'^$',  home, name="home"),
    url(r'^delete-videos/$',  delete_all_videos, name="delete_all_videos"),
    url(r'^remove-youtube-video/$',  remove_youtube_video, name="remove_youtube_video"),
    url(r'^remove-video-entry/(\d+)/(\d+)/$',  remove_video_entry, name="remove_video_entry"),
    url(r'^ajax-foss-based-language-tutorial/$',  ajax_foss_based_language_tutorial,
        name="ajax_foss_based_language_tutorial"),
    url(r'^oauth2callback/$',  auth_return, name="auth_return"),
]
