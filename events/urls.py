from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^$', 'events.views.events_dashboard', name='events_dashboard'),
    url(r'^init/$', 'events.views.init_events_app', name='init_events_app'),
    url(r'^test/$', 'events.views.test', name='test'),
    
    url(r'^ac/$', 'events.views.ac', name='ac'),
    url(r'^ac/new/$', 'events.views.new_ac', name='new_ac'),
    url(r'^ac/(\d+)/edit/$', 'events.views.edit_ac', name='edit_ac'),
    
    #url(r'^xmlparse/$', 'events.views.xmlparse', name='xmlparse'),
    #url(r'^pdf/$', 'events.views.pdf', name='pdf'),
    url(r'^workshop/permission/$', 'events.views.workshop_permission', name='workshop_permission'),
    url(r'^workshop/accessrole/$', 'events.views.accessrole', name='workshop_accessrole'),
    
    url(r'^(?P<role>\w+)/(?P<status>\w+)/$', 'events.views.organiser_invigilator_index', name='organiser_invigilator_index'),
    url(r'^organiser/(?P<status>\w+)/(?P<code>\w+)/(?P<userid>\d+)/$', 'events.views.rp_organiser', name='rp_organiser'),
    
    url(r'^organiser/request/(?P<username>\w+)/$', 'events.views.organiser_request', name='organiser_request'),
    url(r'^organiser/(?P<username>\w+)/edit/$', 'events.views.organiser_edit', name='organiser_edit'),
    url(r'^organiser/view/(?P<username>\w+)/$', 'events.views.organiser_view', name='organiser_view'),

    url(r'^invigilator/(?P<status>\w+)/(?P<code>\w+)/(?P<userid>\d+)/$', 'events.views.rp_invigilator', name='rp_invigilator'),
    url(r'^invigilator/request/(?P<username>\w+)/$', 'events.views.invigilator_request', name='invigilator_request'),
    url(r'^invigilator/(?P<username>\w+)/edit/$', 'events.views.invigilator_edit', name='invigilator_edit'),
    url(r'^invigilator/view/(?P<username>\w+)/$', 'events.views.invigilator_view', name='invigilator_view'),
    
    url(r'^workshop/subscribe/(\w+)/(\d+)/(\d+)/$', 'events.views.student_subscribe', name='student_subscribe'),
    url(r'^workshop/(\d+)/attendance/$', 'events.views.workshop_attendance', name='workshop_attendance'),
    url(r'^workshop/(\d+)/participant/$', 'events.views.workshop_participant', name='workshop_participant'),
    url(r'^workshop/participant/certificate/(\d+)/(\d+)/$', 'events.views.workshop_participant_ceritificate', name='workshop_participant_ceritificate'),
    
    url(r'^workshop/(?P<role>\w+)/request/$', 'events.views.workshop_request', name='workshop_request'),
    url(r'^workshop/(?P<role>\w+)/(?P<rid>\d+)/approvel/$', 'events.views.workshop_approvel', name='workshop_approvel'),
    url(r'^workshop/(?P<role>\w+)/(?P<status>\w+)/$', 'events.views.workshop_list', name='workshop_list'),
    url(r'^workshop/(?P<role>\w+)/(?P<rid>\d+)/edit/$', 'events.views.workshop_edit', name='workshop_edit'),
    
    #url(r'^test/subscribe/(\d+)/(\d+)/$', 'events.views.test_student_subscribe', name='test_student_subscribe'),
    url(r'^test/(\d+)/participant/$', 'events.views.test_participant', name='test_participant'),
    url(r'^test/participant/certificate/(\d+)/(\d+)/$', 'events.views.test_participant_ceritificate', name='test_participant_ceritificate'),
    url(r'^test/(\d+)/attendance/$', 'events.views.test_attendance', name='test_attendance'),
    url(r'^test/(?P<role>\w+)/request/$', 'events.views.test_request', name='test_request'),
    url(r'^test/(?P<role>\w+)/(?P<rid>\d+)/approvel/$', 'events.views.test_approvel', name='test_approvel'),
    url(r'^test/(?P<role>\w+)/(?P<status>\w+)/$', 'events.views.test_list', name='test_list'),
    url(r'^test/(?P<role>\w+)/(?P<rid>\d+)/edit/$', 'events.views.test_edit', name='test_edit'),

    #training
    url(r'^training/participant/certificate/(\d+)/(\d+)/$', 'events.views.training_participant_ceritificate', name='training_participant_ceritificate'),
    url(r'^training/(\d+)/participant/$', 'events.views.training_participant', name='training_participant'),
    url(r'^training/(\d+)/attendance/$', 'events.views.training_attendance', name='training_attendance'),
    url(r'^training/(?P<role>\w+)/request/$', 'events.views.training_request', name='training_request'),
    url(r'^training/(?P<role>\w+)/(?P<rid>\d+)/approvel/$', 'events.views.training_approvel', name='training_approvel'),
    url(r'^training/(?P<role>\w+)/(?P<status>\w+)/$', 'events.views.training_list', name='training_list'),
    url(r'^training/(?P<role>\w+)/(?P<rid>\d+)/edit/$', 'events.views.training_edit', name='training_edit'),
    
    url(r'^delete-notification/(\w+)/(\d+)/$', 'events.views.delete_events_notification', name="delete_events_notification"),
    url(r'^clear-notifications/(\w+)/$', 'events.views.clear_events_notification', name="clear_events_notification"),
    
    #Ajax 
    url(r'ajax-ac-state/$', 'events.views.ajax_ac_state', name='ajax_ac_state'),
    url(r'ajax-ac-location/$', 'events.views.ajax_ac_location', name='ajax_ac_location'),
    url(r'ajax-ac-pincode/$', 'events.views.ajax_ac_pincode', name='ajax_ac_pincode'),
    url(r'ajax-district/$', 'events.views.ajax_district_data', name='ajax_district_data'),
    url(r'ajax-district-collage/$', 'events.views.ajax_district_collage', name='ajax_district_collage'),
    url(r'ajax-dept-foss/$', 'events.views.ajax_dept_foss', name='ajax_dept_foss'),
    url(r'ajax-language/$', 'events.views.ajax_language', name='ajax_language'),
    #url(r'add$', 'events.views.add_contact', name='add_contact'),
    #url(r'edit/(\d+)$', 'events.views.edit_contact', name='edit_contact'),   
    #url(r'delete/(\d+)$', 'events.views.delete_contact', name='delete_contact'),
)
