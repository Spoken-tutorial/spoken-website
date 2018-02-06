from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^videos/$', 'api.views.video_list', name='api_video'),
    url(r'^get_tutorials/(?P<fossid>[0-9]+)/(?P<langid>[0-9]+)/$', 'api.views.get_tutorial_list', name='get_tutorial_list'),
]