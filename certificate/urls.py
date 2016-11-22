from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('certificate.views',
    # Examples:

    url(r'^$', 'index', name='index'),
    url(r'^verify/$', 'verify', name='verify'),
    url(r'^verify/(?P<serial_key>.*)/$', 'verify', name='verify-directly'),
    url(r'^drupal_feedback/$', 'drupal_feedback', name='drupal_feedback'),
    url(r'^drupal_download/$', 'drupal_download', name='drupal_download'),
    url(r'^drupal_workshop_download/$', 'drupal_workshop_download', name='drupal_workshop_download'),
)
