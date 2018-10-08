# Third Party Stuff
from django.conf.urls import patterns, url
app_name = 'reports'
urlpatterns = patterns('',
    url(r'events/training/csv/$', 'reports.views.events_training_csv', name='events_training_csv'),
    url(r'events/test/csv/$', 'reports.views.events_test_csv', name='events_test_csv'),
    url(r'(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/csv/$', 'reports.views.export_csv', name='export_csv'),
    url(r'(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/report/$', 'reports.views.report_filter', name='report_filter'),
    url(r'elibrary/$', 'reports.views.elibrary', name='elibrary'),
)
