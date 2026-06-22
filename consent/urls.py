from django.conf.urls import url

from .views import consent_view

app_name = 'consent'

urlpatterns = [
    url(r'^$', consent_view, name='consent'),
]
