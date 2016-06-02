from __future__ import absolute_import

# Third Party Stuff
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/csv/$', views.export_csv, name='export_csv'),
    url(r'(?P<app_label>[\d\w]+)/(?P<model_name>[\d\w]+)/report/$', views.report_filter, name='report_filter'),
    url(r'elibrary/$', views.elibrary, name='elibrary'),
]
