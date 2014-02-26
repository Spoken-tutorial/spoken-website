from django.conf.urls import patterns, url
from events import views
urlpatterns = patterns('',
	#url(r'^$', views.state, name='state'),
	url(r'states/$', views.state, name='states'),
	url(r'states/new/$', views.new_state, name='new_state'),
	url(r'states/(\d+)/edit/$', views.edit_state, name='edit_state'),
	url(r'update-district$', views.update_district, name='update_district'),
	url(r'check-district$', views.check_district, name='check_district'),
	url(r'update-location$', views.update_location, name='update_location'),
	url(r'update-college$', views.update_college, name='update_college'),
	
    url(r'roles/rp/$', views.roles_rp, name='roles_rp'),
    url(r'roles/rp/new/$', views.new_roles_rp, name='new_roles_rp'),
	url(r'roles/rp/(\d+)/edit/$', views.edit_roles_rp, name='edit_roles_rp'),
    
    url(r'ac/$', views.ac, name='ac'),
    url(r'ac/new/$', views.new_ac, name='new_ac'),
    url(r'ac/(\d+)/edit/$', views.edit_ac, name='edit_ac'),
    
    url(r'organiser/request/(?P<username>\w+)/$', views.organiser_request, name='organiser_request'),
    url(r'organiser/(?P<username>\w+)/edit/$', views.organiser_edit, name='organiser_edit'),
    url(r'organiser/(?P<username>\w+)/$', views.organiser_view, name='organiser_view'),
    #Ajax 
    url(r'ajax-ac-state/$', views.ajax_ac_state, name='ajax_ac_state'),
    url(r'ajax-ac-location/$', views.ajax_ac_location, name='ajax_ac_location'),
    url(r'ajax-ac-pincode/$', views.ajax_ac_pincode, name='ajax_ac_pincode'),
    url(r'ajax-district-collage/$', views.ajax_district_collage, name='ajax_district_collage'),
    #url(r'add$', views.add_contact, name='add_contact'),
    #url(r'edit/(\d+)$', views.edit_contact, name='edit_contact'),   
    #url(r'delete/(\d+)$', views.delete_contact, name='delete_contact'),
)
