# Third Party Stuff
from django.conf.urls import url
from youtube.views import *
from youtube.ajax import *
app_name = 'youtube'
urlpatterns = [ # noqa
    url(r'^$',  home, name="home"),
    url(r'^add-video/$',  add_youtube_video, name="add_youtube_video"),
    url(r'^delete-videos/$',  delete_all_videos, name="delete_all_videos"),
    url(r'^remove-youtube-video/$',  remove_youtube_video, name="remove_youtube_video"),
    url(r'^remove-video-entry/(\d+)/(\d+)/$',  remove_video_entry, name="remove_video_entry"),
    url(r'^ajax-foss-based-language-tutorial/$',  ajax_foss_based_language_tutorial,
        name="ajax_foss_based_language_tutorial"),
    url(r'^ajax/get-uploadable-tutorials/$',  get_uploadable_tutorials, name="get_uploadable_tutorials"),
    url(r'^ajax/get-playlists/$',  get_playlists, name="get_playlists"),
    url(r'^oauth2callback/$',  auth_return, name="auth_return"),
]
