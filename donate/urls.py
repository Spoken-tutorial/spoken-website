from django.conf.urls import include, url
from donate.views import *

app_name = 'donate'

urlpatterns = [
    url(r'^$',  donatehome, name='donatehome'),
    url(r'^initiate_payment/(?P<purpose>\w+)/$',  controller, name='initiate_payment'),
    url(r'send_onetime', send_onetime, name='send_onetime'),
    url(r'validate_user', validate_user, name='validate_user'),
    url(r'validate', validate, name='validate'),
    url(r'receipt', receipt, name='receipt'),
    ]