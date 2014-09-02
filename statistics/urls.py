from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Main pages dispatcher
    url(r'^$', 'statistics.views.maphome', name="maphome"),
    url(r'^india-map/$', 'statistics.views.maphome', name="maphome"),
    url(r'^get-state-info/(\w+)/$', 'statistics.views.get_state_info', name="get_state_info"),
    url(r'^training/$', 'statistics.views.training', name="statistics_training"),
    url(r'^training/(?P<slug>[\w-]+)/$', 'statistics.views.training', name="statistics_training"),
    url(r'^training/(\d+)/participant/$', 'statistics.views.training_participant', name="statistics_training_participant"),
)
