# Third Party Stuff
from django.urls import re_path, path
from django.contrib import admin
from certificate.views import * 

admin.autodiscover()
app_name = 'certificate'
urlpatterns = [
    path(r'', index, name='index'),
    re_path(r'^verify/$', verify, name='verify'),
    re_path(r'^verify/(?P<serial_key>.*)/$', verify, name='verify-directly'),
    re_path(r'^drupal_feedback/$', drupal_feedback, name='drupal_feedback'),
    re_path(r'^drupal_download/$', drupal_download, name='drupal_download'),
    re_path(r'^drupal_workshop_download/$', drupal_workshop_download,
        name='drupal_workshop_download'),

    re_path(r'^koha_massive_workshop/$', koha_massive_workshop_download,
        name='koha_massive_workshop_download'),

     re_path(r'^koha_coordinators_workshop/$', koha_coordinators_workshop_download, 
                name='koha_coordinators_workshop_download'),
    re_path(r'^koha_rc_certificate/$', koha_12octrc_certificate_download,
        name='koha_12octrc_certificate_download'),
    re_path(r'^koha_coordinators_workshop/$', koha_coordinators_workshop_download, 
        name='koha_coordinators_workshop_download'),
    re_path(r'^moodle_coordinators_workshop/$', moodle_coordinators_workshop_download, 
        name='moodle_coordinators_workshop_download'),
    re_path(r'^moodle_massive_workshop/$', moodle_massive_workshop_download,
        name='moodle_massive_workshop_download'),
    re_path(r'^koha_main_workshop/$', koha_main_workshop9march_download,
        name='koha_main_workshop9march_download'),
    re_path(r'^fa_workshop_download/$', fa_workshop_download, name='fa_workshop_download'),
    re_path(r'^itp_workshop_certificate/$', itp_workshop_download, name='itp_workshop_download'),
    re_path(r'^koha_workshop_download/$', koha_workshop_download, name='koha_workshop_download'),
    re_path(r'^koha_9march_rc_certificate/$', koha_9marchrc_certificate_download, name='koha_9marchrc_certificate_download'),
    re_path(r'^moodle_15march_rc_certificate/$', moodle_15marchrc_certificate_download, name='moodle_15marchrc_certificate_download'),
]

