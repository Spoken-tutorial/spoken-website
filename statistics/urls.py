# Third Party Stuff
from django.conf.urls import patterns, url

urlpatterns = patterns('',  # noqa
    url(r'^$', 'statistics.views.maphome', name="maphome"),
    url(r'^india-map/$', 'statistics.views.maphome', name="maphome"),
    url(r'^motion-chart/$', 'statistics.views.motion_chart', name="motion_chart"),
    url(r'^get-state-info/(\w+)/$', 'statistics.views.get_state_info', name="get_state_info"),
    url(r'^training-onlinetest/$', 'statistics.views.training', name="statistics_training"),
    url(r'^training/$', 'statistics.views.training', name="statistic_training"),
    url(r'^tutorial-content/$', 'statistics.views.tutorial_content', name="statistics_content"),

    url(r'^allocate_tutorial/(?P<status>\w+)/$', 'statistics.views.allocate_tutorial', name="allocate_tutorial"),
    url(r'^allocate/(?P<tdid>\w+)/(?P<lid>\w+)/$', 'statistics.views.allocate', name="allocate"),

    url(r'^training/(?P<rid>\d+)/participants/$', 'statistics.views.training_participant',
        name="statistics_training_participants"),
    url(r'^training/(?P<rid>\d+)/participant/students/$', 'statistics.views.studentmaster_ongoing',
        name="statistics_studentmaster_ongoing"),
    
    url(r'^online-test/$', 'statistics.views.online_test', name="statistics_online_test"),
    url(r'^onlinetest/(?P<rid>\d+)/participants/$', 'statistics.views.test_participant',
        name="statistics_test_participants"),
    url(r'^academic-center/$', 'statistics.views.academic_center', name="acdemic_center"),
    url(r'^academic-center/(?P<academic_id>\d+)/$', 'statistics.views.academic_center_view',
        name="academic_center_view"),
    url(r'^academic-center/(?P<academic_id>\d+)/(?P<slug>[\w-]+)/$', 'statistics.views.academic_center_view',
        name="academic_center_view"),
    url(r'^learners/$', 'statistics.views.learners', name="learners"),
    url(r'^pmmmnmtt/fdp/$', 'statistics.views.fdp_training', name="fdp_training"),
)
