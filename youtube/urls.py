# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Third Party Stuff
from django.conf.urls import url

urlpatterns = [
    # Main pages dispatcher
    url(r'^$', 'youtube.views.home', name="home"),
    url(r'^delete-videos/$', 'youtube.views.delete_all_videos', name="delete_all_videos"),
    url(r'^remove-youtube-video/$', 'youtube.views.remove_youtube_video', name="remove_youtube_video"),
    url(r'^remove-video-entry/(\d+)/(\d+)/$',
        'youtube.views.remove_video_entry', name="remove_video_entry"),
    url(r'^ajax-foss-based-language-tutorial/$', 'youtube.views.ajax_foss_based_language_tutorial',
        name="ajax_foss_based_language_tutorial"),
    url(r'^oauth2callback/(\w+)/$', 'youtube.views.auth_return', name="auth_return"),
]
