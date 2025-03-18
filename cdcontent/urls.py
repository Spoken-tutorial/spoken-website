# Third Party Stuff
from django.urls import re_path, path
from cdcontent.views import *
app_name = 'cdcontent'
urlpatterns = [
    # Main pages dispatcher
    path(r'',  home, name="cdcontenthome"),
    re_path(r'^ajax-fill-languages/$',  ajax_fill_languages, name="ajax_fill_languages"),
    re_path(r'^ajax-add-foss/$',  ajax_add_foss, name="ajax_add_foss"),
    re_path(r'^ajax-show-added-foss/$',  ajax_show_added_foss, name="ajax_show_added_foss"),
    re_path(r'^create_cd_download/(\w+)/', internal_computation, name="create_cd_download"),
]
