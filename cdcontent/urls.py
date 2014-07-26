from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Main pages dispatcher
    url(r'^$', 'cdcontent.views.home', name="cdcontenthome"),
    url(r'^ajax-fill-languages/$', 'cdcontent.views.ajax_fill_languages', name="ajax_fill_languages"),
    url(r'^ajax-add-foss/$', 'cdcontent.views.ajax_add_foss', name="ajax_add_foss"),
    url(r'^ajax-show-added-foss/$', 'cdcontent.views.ajax_show_added_foss', name="ajax_show_added_foss"),
)
