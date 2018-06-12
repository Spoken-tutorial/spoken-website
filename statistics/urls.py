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

    url(r'^allocate_tutorial/(?P<sel_status>\w+)/$', 'statistics.views.allocate_tutorial', name="allocate_tutorial"),
    url(r'^allocate_tutorial_manager/(?P<sel_status>\w+)/$', 'statistics.views.allocate_tutorial', name="allocate_tutorial"),
    url(r'^revoke_allocated_tutorial/(?P<uid>\w+)/(?P<lid>\w+)/(?P<tdid>\w+)/(?P<taid>\w+)$', 'statistics.views.revoke_allocated_tutorial', name="revoke_allocated_tutorial"),
    url(r'^extend/(\w+)/$', 'statistics.views.extend_submission_date', name="extend_submission_date"),
    url(r'^allocate/(?P<tdid>\d+)/(?P<lid>\d+)/(?P<uname>\w+)$', 'statistics.views.allocate', name="allocate"),
    url(r'^allocate_foss/(?P<fid>\d+)/(?P<lang>\w+)/(?P<uname>\w+)/$', 'statistics.views.allocate_foss', name="allocate_foss"),
    url(r'^refresh_contributors/$', 'statistics.views.refresh_contributors', name="refresh_contributors"),
    url(r'^get_languages/(?P<uid>\w+)$', 'statistics.views.get_languages', name="get_languages"),
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

    url(r'^refresh_tutorials/$','statistics.views.refresh_tutorials',name = "refresh_tutorials")
)
