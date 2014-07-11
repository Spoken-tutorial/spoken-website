from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    #url(r'^$', 'creation.views.creationhome', name="creationhome"),
    url(r'^users/$', 'creationmigrate.views.users', name="users"),
    url(r'^foss/$', 'creationmigrate.views.foss_categories', name="foss_categories"),
    url(r'^languages/$', 'creationmigrate.views.languages', name="languages"),
    url(r'^tutorial-details/$', 'creationmigrate.views.tutorial_details', name="tutorial_details"),
    url(r'^tutorial-resources/$', 'creationmigrate.views.tutorial_resources', name="tutorial_resources"),
    #url(r'^tutorial-common-contents/$', 'creationmigrate.views.tutorial_common_contents', name="tutorial_common_contents"),
    url(r'^test/$', 'creationmigrate.views.test', name="test"),

)
