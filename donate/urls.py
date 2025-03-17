from django.urls import path, re_path
from donate.views import *
from .subscription import get_academic_centers
app_name = 'donate'

urlpatterns = [
    path(r'',  donatehome, name='donatehome'),
    re_path(r'^initiate_payment/(?P<purpose>\w+)/$',  controller, name='initiate_payment'),
    re_path(r'send_onetime', send_onetime, name='send_onetime'),
    re_path(r'validate_user', validate_user, name='validate_user'),
    re_path(r'validate', validate, name='validate'),
    re_path(r'receipt', receipt, name='receipt'),
    re_path(r'pay_now/(?P<purpose>\w+)/$', pay_now,name='pay_now'),
    re_path(r'school', school_donation, name='school_donation'),
    re_path(r'get_academic_centers/', get_academic_centers, name='get_academic_centers'),
    ]