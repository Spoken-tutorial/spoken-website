# Third Party Stuff
from django.urls import re_path, path
from masquerade.views import *
app_name = 'masquerade'
urlpatterns = [
    path(r'',  masquerade_home, name="masquerade_home"),
    re_path(r'^mask/(\d+)/$',  mask, name="mask"),
    re_path(r'^unmask/$',  unmask),
]
