# Third Party Stuff
from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('certificate.views',  # noqa
    url(r'^$', 'index', name='index'),
    url(r'^verify/$', 'verify', name='verify'),
    url(r'^verify/(?P<serial_key>.*)/$', 'verify', name='verify-directly'),
    url(r'^drupal_feedback/$', 'drupal_feedback', name='drupal_feedback'),
    url(r'^drupal_download/$', 'drupal_download', name='drupal_download'),
    url(r'^drupal_workshop_download/$', 'drupal_workshop_download',
        name='drupal_workshop_download'),
    url(r'^fa_workshop_download/$', 'fa_workshop_download',
        name='fa_workshop_download'),
    url(r'^itp_workshop_certificate/$', 'itp_workshop_download',
        name='itp_workshop_download'),
    url(r'^koha_workshop_download/$', 'koha_workshop_download',
        name='koha_workshop_download'),
    url(r'^koha_massive_workshop/$', 'koha_massive_workshop_download',
        name='koha_massive_workshop_download'),
    url(r'^koha_rc_certificate/$', 'koha_rc_certificate_download',
        name='koha_rc_certificate_download'),
    url(r'^koha_coordinators_workshop/$', 'koha_coordinators_workshop_download', 
        name='koha_coordinators_workshop_download'),
    url(r'^moodle_coordinators_workshop/$', 'moodle_coordinators_workshop_download', 
        name='moodle_coordinators_workshop_download'),
    url(r'^moodle_massive_workshop/$', 'moodle_massive_workshop_download',
        name='moodle_massive_workshop_download'),

)
