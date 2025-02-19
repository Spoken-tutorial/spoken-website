from django.conf.urls import include, url
from donate.views import *
from .subscription import get_academic_centers
app_name = 'donate'

urlpatterns = [
    url(r'^$',  donatehome, name='donatehome'),
    url(r'^initiate_payment/(?P<purpose>\w+)/$',  controller, name='initiate_payment'),
    url(r'send_onetime', send_onetime, name='send_onetime'),
    url(r'validate_user', validate_user, name='validate_user'),
    url(r'validate', validate, name='validate'),
    url(r'receipt', receipt, name='receipt'),
    url(r'pay_now/(?P<purpose>\w+)/$', pay_now,name='pay_now'),
    url(r'school', school_donation, name='school_donation'),
    url(r'get_academic_centers/', get_academic_centers, name='get_academic_centers'),
    ]