from django.urls import re_path
from api.views import *

app_name = 'api'

urlpatterns = [
    re_path(r'^videos/$', video_list, name='api_video'),
    re_path(r'^get_tutorials/(?P<fossid>[0-9]+)/(?P<langid>[0-9]+)/$', get_tutorial_list, name='get_tutorial_list'),
    re_path(r'^show_categories/$', show_categories, name='show_categories'),
    re_path(r'^get_fosslist/$', get_fosslist, name='get_fosslist'),
    re_path(r'^get_schoolfosslist/$', get_schoolfosslist, name='get_schoolfosslist'),
    re_path(r'^get_fosslanguage/(?P<fossid>[0-9]+)/$', get_fosslanguage, name='get_fosslanguage'),
    re_path(r'^get_tutorialdetails/(?P<tutid>[0-9]+)/$', get_tutorialdetails, name='get_tutorialdetails'),
    re_path(r'^spoken_tutorial_videos/$', RelianceJioAPI.as_view(), name ='reliancejioapi'),
    re_path(r'^st_video_resource/$', TutorialResourceAPI.as_view(), name ='st_video_resource'),
    re_path(r'^script/foss_lang/$', get_all_foss_langauges, name='script_foss_lang'),
    re_path(r'^script/tutorials/(?P<fid>[0-9]+)/(?P<lid>[0-9]+)/$', get_all_tutorials, name='script_foss_lang'),
    re_path(r'^script/roles/(?P<fid>[0-9]+)/(?P<lid>[0-9]+)/(?P<username>[\w\-]+)/$', get_foss_roles, name='script_foss_roles'),
    re_path(r'^script/tutorial_detail/(?P<fid>[0-9]+)/(?P<lid>[0-9]+)/(?P<tid>[0-9]+)/$', get_tutorial_detail, name='script_tutorial_detail'),
    re_path(r'^get_users_progress/$', get_users_progress, name='get_users_progress'),
    re_path(r'^get_top_tuts_foss/$', get_top_tuts_foss, name='get_top_tuts_foss'),
]
