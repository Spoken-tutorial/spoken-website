# Third Party Stuff
from django.conf.urls import url
from masquerade.views import *
app_name = 'masquerade'
urlpatterns = [
    url(r'^$',  masquerade_home, name="masquerade_home"),
    url(r'^mask/(\d+)/$',  mask, name="mask"),
    url(r'^unmask/$',  unmask),
]
