# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

# Third Party Stuff
from django.conf.urls import url

urlpatterns = [
    # Main pages dispatcher
    url(r'^$', 'statistics.views.maphome', name="maphome"),
    url(r'^india-map/$', 'statistics.views.maphome', name="maphome"),
    url(r'^motion-chart/$', 'statistics.views.motion_chart', name="motion_chart"),
    url(r'^get-state-info/(\w+)/$', 'statistics.views.get_state_info', name="get_state_info"),
    url(r'^training-onlinetest/$', 'statistics.views.training', name="statistics_training"),
    url(r'^training/$', 'statistics.views.training', name="statistic_training"),
    url(r'^training/(?P<rid>\d+)/participants/$',
        'statistics.views.training_participant', name="statistics_training_participants"),
    url(r'^online-test/$', 'statistics.views.online_test', name="statistics_online_test"),
    url(r'^onlinetest/(?P<rid>\d+)/participants/$',
        'statistics.views.test_participant', name="statistics_test_participants"),
    url(r'^academic-center/$', 'statistics.views.academic_center', name="acdemic_center"),
    url(r'^academic-center/(?P<academic_id>\d+)/$',
        'statistics.views.academic_center_view', name="academic_center_view"),
    url(r'^academic-center/(?P<academic_id>\d+)/(?P<slug>[\w-]+)/$',
        'statistics.views.academic_center_view', name="academic_center_view"),
    url(r'^learners/$', 'statistics.views.learners', name="learners"),
]
