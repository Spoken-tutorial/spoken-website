from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Main pages dispatcher
    url(r'^$', 'cdcontent.views.home', name="cdcontenthome"),
    url(r'^ajax-fill-languages/$', 'cdcontent.views.ajax_fill_languages', name="ajax_fill_languages"),
)
