# -*- coding: utf-8 -*-
from django.urls import re_path, path

from . import views


urlpatterns = [
    re_path(r'^stop/$',
        views.stop_impersonate,
        name='impersonate-stop'),
    re_path(r'^list/$',
        views.list_users,
        {'template': 'impersonate/list_users.html'},
        name='impersonate-list'),
    re_path(r'^search/$',
        views.search_users,
        {'template': 'impersonate/search_users.html'},
        name='impersonate-search'),
    re_path(r'^(?P<uid>.+)/$',
        views.impersonate,
        name='impersonate-start'),
    path(r'^$', views.impersonate_home,
        name="impersonate_home"),
]
