# Third Party Stuff
from django.conf.urls import  url
from django.contrib import admin
from certificate.views import * 

admin.autodiscover()
app_name = 'certificate'
urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^verify/$', verify, name='verify'),
    url(r'^verify/(?P<serial_key>.*)/$', verify, name='verify-directly'),
    url(r'^drupal_feedback/$', drupal_feedback, name='drupal_feedback'),
    url(r'^drupal_download/$', drupal_download, name='drupal_download'),
    url(r'^drupal_workshop_download/$', drupal_workshop_download,
        name='drupal_workshop_download'),
    url(r'^fa_workshop_download/$', fa_workshop_download, name='fa_workshop_download'),
    url(r'^itp_workshop_certificate/$', itp_workshop_download, name='itp_workshop_download'),
    url(r'^koha_workshop_download/$', koha_workshop_download, name='koha_workshop_download'),
]
