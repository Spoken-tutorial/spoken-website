from django.conf.urls import url
from api.views import *

app_name = 'api'

urlpatterns = [
    url(r'^videos/$', video_list, name='api_video'),
    url(r'^get_tutorials/(?P<fossid>[0-9]+)/(?P<langid>[0-9]+)/$', get_tutorial_list, name='get_tutorial_list'),
    url(r'^show_categories/$', show_categories, name='show_categories'),
    url(r'^get_fosslist/$', get_fosslist, name='get_fosslist'),
    url(r'^get_schoolfosslist/$', get_schoolfosslist, name='get_schoolfosslist'),
    url(r'^get_fosslanguage/(?P<fossid>[0-9]+)/$', get_fosslanguage, name='get_fosslanguage'),
    url(r'^get_tutorialdetails/(?P<tutid>[0-9]+)/$', get_tutorialdetails, name='get_tutorialdetails'),
    url(r'^spoken_tutorial_videos/$', RelianceJioAPI.as_view(), name ='reliancejioapi')
]
