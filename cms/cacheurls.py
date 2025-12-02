from django.conf.urls import url
from cms import views

urlpatterns = [
    url(r'^cache-tools/$', views.cache_tools, name='cache-tools'),
]
