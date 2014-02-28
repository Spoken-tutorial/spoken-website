from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	# Main pages dispatcher
	url(r'^$', 'creation.views.creationhome', name="creationhome"),
	url(r'^upload_tutorial/$', 'creation.views.upload_tutorial_index', name="upload_tutorial_index"),
	url(r'^upload_tutorial/(\d+)/(\d+)/$', 'creation.views.upload_tutorial', name="upload_tutorial"),
	url(r'^upload_component/(\d+)/(\w+)/$', 'creation.views.upload_component', name="upload_component"),
	url(r'^ajax_upload_foss/$', 'creation.views.ajax_upload_foss', name="ajax_upload_foss"),
	url(r'^testingvis/$', 'creation.views.testingvis', name="testingvis"),
)
