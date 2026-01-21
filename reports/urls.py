# Third Party Stuff
from django.conf.urls import url
from reports.views import *
app_name = 'reports'
urlpatterns = [
    url(r'events/training/csv/$',  events_training_csv, name='events_training_csv'),
    url(r'events/test/csv/$',  events_test_csv, name='events_test_csv'),
    url(r'(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/csv/$',  export_csv, name='export_csv'),
    url(r'(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/report/$',  report_filter, name='report_filter'),
    url(r'elibrary/$',  elibrary, name='elibrary'),
    url(r'api_search_engine/$',  api_search_engine, name='api_search'),
    
]
