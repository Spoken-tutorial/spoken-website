# Third Party Stuff
from django.urls import re_path, path
from statistics.views import *
app_name = 'statistics'
urlpatterns =  [ # noqa
    path(r'',  maphome, name="maphome"),
    re_path(r'^india-map/$',  maphome, name="maphome"),
    re_path(r'^motion-chart/$',  motion_chart, name="motion_chart"),
    re_path(r'^get-state-info/(\w+)/$',  get_state_info, name="get_state_info"),
    re_path(r'^training-onlinetest/$',  training, name="statistics_training"),
    re_path(r'^training/$',  training, name="statistic_training"),
    re_path(r'^tutorial-content/$',  tutorial_content, name="statistics_content"),
    re_path(r'^training/(?P<rid>\d+)/participants/$',  training_participant,
        name="statistics_training_participants"),
    re_path(r'^training/(?P<rid>\d+)/participant/students/$',  studentmaster_ongoing,
        name="statistics_studentmaster_ongoing"),
    
    re_path(r'^online-test/$',  online_test, name="statistics_online_test"),
    re_path(r'^onlinetest/(?P<rid>\d+)/participants/$',  test_participant,
        name="statistics_test_participants"),
    re_path(r'^academic-center/$',  academic_center, name="acdemic_center"),
    re_path(r'^academic-center/(?P<academic_id>\d+)/$',  academic_center_view,
        name="academic_center_view"),
    re_path(r'^academic-center/(?P<academic_id>\d+)/(?P<slug>[\w-]+)/$',  academic_center_view,
        name="academic_center_view"),
    re_path(r'^learners/$',  learners, name="learners"),
    re_path(r'^pmmmnmtt/fdp/$',  fdp_training, name="fdp_training"),
    re_path(r'^ilw/$',  ilw_stats, name="ilw_stats"),

]