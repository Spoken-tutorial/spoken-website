# Third Party Stuff
from django.urls import re_path
app_name = 'cdcontent'
urlpatterns = [
    # Main pages dispatcher
    re_path(r'^$', 'cdcontent.views.home', name="cdcontenthome"),
    re_path(r'^ajax-fill-languages/$', 'cdcontent.views.ajax_fill_languages', name="ajax_fill_languages"),
    re_path(r'^ajax-add-foss/$', 'cdcontent.views.ajax_add_foss', name="ajax_add_foss"),
    re_path(r'^ajax-show-added-foss/$', 'cdcontent.views.ajax_show_added_foss', name="ajax_show_added_foss"),
]
