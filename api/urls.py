from django.conf.urls import url
from api.views import *

app_name = 'api'

urlpatterns = [
    url(r'^videos/$', video_list, name='api_video'),
    url(r'^get_tutorials/(?P<fossid>[0-9]+)/(?P<langid>[0-9]+)/$', get_tutorial_list, name='get_tutorial_list'),
]