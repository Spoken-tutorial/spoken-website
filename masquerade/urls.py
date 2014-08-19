from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'masquerade.views.masquerade_home', name="masquerade_home"),
    url(r'^mask/(\d+)/$', 'masquerade.views.mask', name="mask"),
    url(r'^unmask/$', 'masquerade.views.unmask'),
)
