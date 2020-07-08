# Third Party Stuff
from django.conf.urls import url
from cdcontent.views import *
app_name = 'cdcontent'
urlpatterns = [
    # Main pages dispatcher
    url(r'^$',  home, name="cdcontenthome"),
    url(r'^ajax-fill-languages/$',  ajax_fill_languages, name="ajax_fill_languages"),
    url(r'^ajax-add-foss/$',  ajax_add_foss, name="ajax_add_foss"),
    url(r'^ajax-show-added-foss/$',  ajax_show_added_foss, name="ajax_show_added_foss"),
    url(r'^create_cd_download/(\w+)/', internal_computation, name="create_cd_download"),
]
