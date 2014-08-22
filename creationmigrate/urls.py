from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    #url(r'^$', 'creation.views.creationhome', name="creationhome"),
    url(r'^users/$', 'creationmigrate.views.users', name="users"),
    url(r'^foss/$', 'creationmigrate.views.foss_categories', name="foss_categories"),
    url(r'^languages/$', 'creationmigrate.views.languages', name="languages"),
    url(r'^tutorial-details/$', 'creationmigrate.views.tutorial_details', name="tutorial_details"),
    url(r'^tutorial-resources/$', 'creationmigrate.views.tutorial_resources', name="tutorial_resources"),
    url(r'^admin-reviewer-roles/$', 'creationmigrate.views.admin_reviewer_roles', name="admin_reviewer_roles"),
    url(r'^domain-reviewer-roles/$', 'creationmigrate.views.domain_reviewer_roles', name="domain_reviewer_roles"),
    url(r'^quality-reviewer-roles/$', 'creationmigrate.views.quality_reviewer_roles', name="quality_reviewer_roles"),
    url(r'^fix-tutorial-resources-status/$', 'creationmigrate.views.fix_tutorial_resources_status', name="fix_tutorial_resources_status"),
    url(r'^create-thumbnails/$', 'creationmigrate.views.create_thumbnails', name="create_thumbnails"),
    #url(r'^tutorial-common-contents/$', 'creationmigrate.views.tutorial_common_contents', name="tutorial_common_contents"),
    url(r'^srtfiles/$', 'creationmigrate.views.srtfiles', name="srtfiles"),
    url(r'^test/$', 'creationmigrate.views.test', name="test"),
)
