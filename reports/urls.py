# Third Party Stuff
from django.urls import re_path
from reports.views import *
app_name = 'reports'
urlpatterns = [
    re_path(r'events/training/csv/$',  events_training_csv, name='events_training_csv'),
    re_path(r'events/test/csv/$',  events_test_csv, name='events_test_csv'),
    re_path(r'(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/csv/$',  export_csv, name='export_csv'),
    re_path(r'(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/report/$',  report_filter, name='report_filter'),
    re_path(r'elibrary/$',  elibrary, name='elibrary'),
]
