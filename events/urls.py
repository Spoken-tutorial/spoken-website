from django.conf.urls import patterns, url
from events import views
urlpatterns = patterns('',
	#url(r'^$', views.state, name='state'),
	url(r'test/$', views.test, name='test'),
	
	url(r'^ac/$', views.ac, name='ac'),
	url(r'^ac/new/$', views.new_ac, name='new_ac'),
	url(r'^ac/(\d+)/edit/$', views.edit_ac, name='edit_ac'),
	
	#url(r'^xmlparse/$', views.xmlparse, name='xmlparse'),
	
	url(r'^organiser/(?P<status>\w+)/$', views.rp_organiser, name='rp_organiser'),
	url(r'^organiser/active/(?P<code>\w+)/(?P<userid>\d+)/$', views.rp_organiser_confirm, name='rp_organiser_confirm'),
	url(r'^organiser/block/(?P<code>\w+)/(?P<userid>\d+)/$', views.rp_organiser_block, name='rp_organiser_block'),
	
	
	url(r'^organiser/request/(?P<username>\w+)/$', views.organiser_request, name='organiser_request'),
	url(r'^organiser/(?P<username>\w+)/edit/$', views.organiser_edit, name='organiser_edit'),
	url(r'^organiser/view/(?P<username>\w+)/$', views.organiser_view, name='organiser_view'),

	
	url(r'^invigilator/(?P<status>\w+)/$', views.rp_invigilator, name='rp_invigilator'),
	url(r'^invigilator/active/(?P<code>\w+)/(?P<userid>\d+)/$', views.rp_invigilator_confirm, name='rp_invigilator_confirm'),
	url(r'^invigilator/block/(?P<code>\w+)/(?P<userid>\d+)/$', views.rp_invigilator_block, name='rp_invigilator_block'),
	
	url(r'^invigilator/request/(?P<username>\w+)/$', views.invigilator_request, name='invigilator_request'),
	url(r'^invigilator/(?P<username>\w+)/edit/$', views.invigilator_edit, name='invigilator_edit'),
	url(r'^invigilator/view/(?P<username>\w+)/$', views.invigilator_view, name='invigilator_view'),
	
	url(r'^workshop/(\d+)/participant/$', views.workshop_participant, name='workshop_participant'),
	url(r'^workshop/permission/$', views.workshop_permission, name='workshop_permission'),
	url(r'^workshop/accessrole/$', views.accessrole, name='workshop_accessrole'),
	url(r'^workshop/request/$', views.workshop_request, name='workshop_request'),
	url(r'^workshop/(\d+)/approvel/$', views.workshop_approvel, name='workshop_approvel'),
	url(r'^workshop/(?P<status>\w+)/$', views.workshop_list, name='workshop_list'),
	url(r'^workshop/(\d+)/edit/$', views.workshop_edit, name='workshop_edit'),

	#Ajax 
	url(r'ajax-ac-state/$', views.ajax_ac_state, name='ajax_ac_state'),
	url(r'ajax-ac-location/$', views.ajax_ac_location, name='ajax_ac_location'),
	url(r'ajax-ac-pincode/$', views.ajax_ac_pincode, name='ajax_ac_pincode'),
	url(r'ajax-district/$', views.ajax_district_data, name='ajax_district_data'),
	url(r'ajax-district-collage/$', views.ajax_district_collage, name='ajax_district_collage'),
	#url(r'add$', views.add_contact, name='add_contact'),
	#url(r'edit/(\d+)$', views.edit_contact, name='edit_contact'),   
	#url(r'delete/(\d+)$', views.delete_contact, name='delete_contact'),
)
