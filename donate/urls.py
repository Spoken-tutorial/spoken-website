from django.conf.urls import include, url
from donate.views import *

app_name = 'donate'

urlpatterns = [
    url(r'^$',  donatehome, name='donatehome'),
    url(r'^initiate_payment$',  controller, name='initiate_payment'),
    ]