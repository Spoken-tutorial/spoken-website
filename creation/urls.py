from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # Main pages dispatcher
    url(r'^$', 'creation.views.creationhome', name="creationhome"),
    # Contributor part
    url(r'^upload-tutorial/$', 'creation.views.upload_tutorial_index', name="upload_tutorial_index"),
    url(r'^upload-tutorial/(\d+)/$', 'creation.views.upload_tutorial', name="upload_tutorial"),
    url(r'^upload-component/(\d+)/(\w+)/$', 'creation.views.upload_component', name="upload_component"),
    url(r'^upload-outline/(\d+)/$', 'creation.views.upload_outline', name="upload_outline"),
    url(r'^upload-script/(\d+)/$', 'creation.views.upload_script', name="upload_script"),
    url(r'^mark-notrequired/(\d+)/(\w+)/$', 'creation.views.mark_notrequired', name="mark_notrequired"),
    url(r'^view-outline/(\d+)/$', 'creation.views.view_outline', name="view_outline"),
    url(r'^view-video/(\d+)/$', 'creation.views.view_video', name="view_video"),
    url(r'^tutorials-contributed/$', 'creation.views.tutorials_contributed', name="tutorials_contributed"),
    url(r'^ajax-upload-foss/$', 'creation.views.ajax_upload_foss', name="ajax_upload_foss"),
    # Admin Reviewer part
    url(r'^admin-review/$', 'creation.views.admin_review_index', name="admin_review_index"),
    url(r'^review-video/(\d+)/$', 'creation.views.review_video', name="review_video"),
    # Domain Reviewer part
    url(r'^domain-review/$', 'creation.views.domain_review_index', name="domain_review_index"),
    url(r'^domain-review-tutorial/(\d+)/$', 'creation.views.domain_review_tutorial', name="domain_review_tutorial"),
    url(r'^domain-review-component/(\d+)/(\w+)/$', 'creation.views.domain_review_component', name="domain_review_component"),
    # Quality Reviewer part
    url(r'^quality-review/$', 'creation.views.quality_review_index', name="quality_review_index"),
    url(r'^quality-review-tutorial/(\d+)/$', 'creation.views.quality_review_tutorial', name="quality_review_tutorial"),
    url(r'^quality-review-component/(\d+)/(\w+)/$', 'creation.views.quality_review_component', name="quality_review_component"),
    url(r'^publish-tutorial/(\d+)/$', 'creation.views.publish_tutorial', name="publish_tutorial"),
    url(r'^accept-all/(\w+)/(\d+)/$', 'creation.views.accept_all', name="accept_all"),

    url(r'^testingvis/$', 'creation.views.testingvis', name="testingvis"),
)
