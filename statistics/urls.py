# Third Party Stuff
from django.conf.urls import url
from statistics.views import *
app_name = 'statistics'
urlpatterns =  [ # noqa
    url(r'^$',  maphome, name="maphome"),
    url(r'^india-map/$',  maphome, name="maphome"),
    url(r'^motion-chart/$',  motion_chart, name="motion_chart"),
    url(r'^get-state-info/(\w+)/$',  get_state_info, name="get_state_info"),
    url(r'^training-onlinetest/$',  training, name="statistics_training"),
    url(r'^training/$',  training, name="statistic_training"),
    url(r'^tutorial-content/$',  tutorial_content, name="statistics_content"),
    url(r'^training/(?P<rid>\d+)/participants/$',  training_participant,
        name="statistics_training_participants"),
    url(r'^training/(?P<rid>\d+)/participant/students/$',  studentmaster_ongoing,
        name="statistics_studentmaster_ongoing"),
    
    url(r'^online-test/$',  online_test, name="statistics_online_test"),
    url(r'^onlinetest/(?P<rid>\d+)/participants/$',  test_participant,
        name="statistics_test_participants"),
    url(r'^academic-center/$',  academic_center, name="acdemic_center"),
    url(r'^academic-center/(?P<academic_id>\d+)/$',  academic_center_view,
        name="academic_center_view"),
    url(r'^academic-center/(?P<academic_id>\d+)/(?P<slug>[\w-]+)/$',  academic_center_view,
        name="academic_center_view"),
    url(r'^learners/$',  learners, name="learners"),
    url(r'^pmmmnmtt/fdp/$',  fdp_training, name="fdp_training"),
    url(r'^ilw/$',  ilw_stats, name="ilw_stats"),

]