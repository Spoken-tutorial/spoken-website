# Third Party Stuff
from django.urls import re_path
from youtube.views import *
app_name = 'youtube'
urlpatterns = [ # noqa
    url(r'',  home, name="home"),
    re_path(r'^delete-videos/$',  delete_all_videos, name="delete_all_videos"),
    re_path(r'^remove-youtube-video/$',  remove_youtube_video, name="remove_youtube_video"),
    re_path(r'^remove-video-entry/(\d+)/(\d+)/$',  remove_video_entry, name="remove_video_entry"),
    re_path(r'^ajax-foss-based-language-tutorial/$',  ajax_foss_based_language_tutorial,
        name="ajax_foss_based_language_tutorial"),
    re_path(r'^oauth2callback/$',  auth_return, name="auth_return"),
]
