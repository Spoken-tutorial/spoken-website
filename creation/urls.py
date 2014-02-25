from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	# Main pages dispatcher
	# url(r'^$', 'creation.views.creationhome', name="home"),
	# url(r'^add_language/$', 'creation.views.add_language', name="add_language"),
	# url(r'^add_foss/$', 'creation.views.add_foss', name="add_foss"),
	url(r'^upload_tutorial/$', 'creation.views.upload_tutorial', name="upload_tutorial"),
	url(r'^testingvis/$', 'creation.views.testingvis', name="testingvis"),
	url(r'^ajax_upload_foss/$', 'creation.views.ajax_upload_foss', name="ajax_upload_foss"),
)
