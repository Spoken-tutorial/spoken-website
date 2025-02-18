from django.conf.urls import url, include
from events.views import *
from events.notification import nemail
app_name = 'events'
urlpatterns = [
    url(r'^$',  events_dashboard, name='events_dashboard'),
    url(r'^init/$',  init_events_app, name='init_events_app'),
    
    #cron job
    #todo: test and workshop auto close
    url(r'^fix-date-for-first-training/$',  fix_date_for_first_training, name='fix_date_for_first_training'),
    #url(r'^training-gentle-reminder/$',  training_gentle_reminder', name='training_gentle_reminder'),
    #url(r'^training-completion-reminder/$',  training_completion_reminder', name='training_completion_reminder'),
    url(r'^close-predated-ongoing-workshop/$',  close_predated_ongoing_workshop, name='close_predated_ongoing_workshop'),
    url(r'^close-predated-ongoing-test/$',  close_predated_ongoing_test, name='close_predated_ongoing_test'),
    
    url(r'^test/$', nemail, name='test'),
    
    url(r'^ac/$',  ac, name='ac'),
    url(r'^ac/new/$',  new_ac, name='new_ac'),
    url(r'^ac/(\d+)/edit/$',  edit_ac, name='edit_ac'),
    
    #url(r'^xmlparse/$',  xmlparse', name='xmlparse'),
    #url(r'^pdf/$',  pdf', name='pdf'),
    url(r'^training/permission/$',  training_permission, name='training_permission'),
    url(r'^training/accessrole/$',  accessrole, name='training_accessrole'),
    url(r'^training/old-training-attendance/$',  old_training_attendance, name='old_training_attendance'),
    url(r'^training/old-training-attendance-upload/(\d+)/$',  old_training_attendance_upload, name='old_training_attendance_upload'),
    
    url(r'^(?P<role>\w+)/(?P<status>\w+)/$',  organiser_invigilator_index, name='organiser_invigilator_index'),
    url(r'^organiser/(?P<status>\w+)/(?P<code>\w+)/(?P<userid>\d+)/$',  rp_organiser, name='rp_organiser'),
    url(r'^organiser-handover/$', handover, name='handover'),
    
    url(r'^activate-academics/$',  activate_academics, name='activate_academics'),
    url(r'^activate-academics-org/(?P<academic_id>\d+)/$',  activate_academic_org, name='activate_academic_org'),

    url(r"^accountexecutive/request/(?P<username>[\w. @-]+)/$",  accountexecutive_request, name='accountexecutive_request'),
    url(r"^accountexecutive/view/(?P<username>[\w. @-]+)/$",  accountexecutive_view, name='accountexecutive_view'),
    url(r"^accountexecutive/(?P<username>[\w. @-]+)/edit/$",  accountexecutive_edit, name='accountexecutive_edit'),
    url(r'^accountexecutive/(?P<status>\w+)/(?P<code>\w+)/(?P<userid>\d+)/$',  rp_accountexecutive, name='rp_accountexecutive'),
    
    url(r"^organiser/request/(?P<username>[\w. @-]+)/$",  organiser_request, name='organiser_request'),
    url(r"^organiser/(?P<username>[\w. @-]+)/edit/$",  organiser_edit, name='organiser_edit'),
    url(r"^organiser/view/(?P<username>[\w. @-]+)/$",  organiser_view, name='organiser_view'),

    url(r'^invigilator/(?P<status>\w+)/(?P<code>\w+)/(?P<userid>\d+)/$',  rp_invigilator, name='rp_invigilator'),
    url(r"^invigilator/request/(?P<username>[\w. @-]+)/$",  invigilator_request, name='invigilator_request'),
    url(r"^invigilator/(?P<username>[\w. @-]+)/edit/$",  invigilator_edit, name='invigilator_edit'),
    url(r"^invigilator/view/(?P<username>[\w. @-]+)/$",  invigilator_view, name='invigilator_view'),
    
    #live feedback
    url(r'^training/live/list/$',  live_training, name='live_training'),
    url(r'^training/live/list/(\d+)/$',  live_training, name='live_training'),
    
    url(r'^training/subscribe/(\w+)/(\d+)/(\d+)/$',  training_subscribe, name='student_subscribe'),
    url(r'^training/(\d+)/attendance/$',  training_attendance, name='training_attend'),
    url(r'^training/(\d+)/participant/$',  training_participant, name='training_participant'),
    url(r'^training/participant/certificate/(\d+)/(\d+)/$',  training_participant_ceritificate, name='training_participant_ceritificate'),
    url(r'^training/participant/feedback/(\d+)/(\d+)/$',  training_participant_feedback, name='training_participant_feedback'),
    
    #live feedback
     url(r'^training/participant/lfeedback/(\d+)/(\d+)/$',  training_participant_viewlivefeedback, name='training_participant_viewlivefeedback'),
    url(r'^training/participant/lfeedback/(\d+)/$',  training_participant_livefeedback, name='training_participant_livefeedback'),
    
    #language Feedback
    #url(r'^training/participant/language-feedback/(\d+)/(\d+)/$',  training_participant_view_language_feedback', name='training_participant_viewlivefeedback'),
    url(r'^training/participant/language-feedback/(\d+)/(\d+)/$',  training_participant_language_feedback, name='training_participant_language_feedback'),
    
    url(r'^training/(?P<role>\w+)/request/$',  training_request, name='training_request'),
    url(r'^training/(?P<role>\w+)/clone/$',  training_clone, name='training_clone'),
    url(r'^training/(?P<role>\w+)/(?P<rid>\d+)/approvel/$',  training_approvel, name='training_approvel'),
    url(r'^training/(?P<role>\w+)/(?P<status>\w+)/$',  training_list, name='training_list'),
    url(r'^training/(?P<role>\w+)/(?P<rid>\d+)/edit/$',  training_request, name='training_edit'),
    url(r'^training/(?P<role>\w+)/(?P<rid>\d+)/clone/$',  training_clone, name='training_clone'),
    #url(r'^training/training-completion/(?P<rid>\d+)/$',  training_completion', name="training_completion"),
    url(r'^training/view/training-completion/(?P<rid>\d+)/$',  view_training_completion, name="view_training_completion"),
    
    #url(r'^test/subscribe/(\d+)/(\d+)/$',  test_student_subscribe', name='test_student_subscribe'),
    url(r'^test/(\d+)/participant/$',  test_participant, name='test_participant'),
    url(r'^test/participant/certificate/(\d+)/(\d+)/$',  test_participant_ceritificate, name='test_participant_ceritificate'),
    url(r'^test/participant/certificate/all/(\d+)/$',  test_participant_ceritificate_all, name='test_participant_ceritificate_all'),
    url(r'^test/(\d+)/attendance/$',  test_attendance, name='test_attendance'),
    url(r'^test/(?P<role>\w+)/request/$',  test_request, name='test_request'),
    url(r'^test/(?P<role>\w+)/(?P<rid>\d+)/approvel/$',  test_approvel, name='test_approvel'),
    url(r'^test/(?P<role>\w+)/(?P<status>\w+)/$',  test_list, name='test_list'),
    url(r'^test/(?P<role>\w+)/(?P<rid>\d+)/edit/$',  test_request, name='test_request'),
    url(r'^test/verify-test-certificate/$', verify_test_certificate, name='verify_test_certificate'),

    url(r'^delete-notification/(\w+)/(\d+)/$',  delete_events_notification, name="delete_events_notification"),
    url(r'^clear-notifications/(\w+)/$',  clear_events_notification, name="clear_events_notification"),
    
    url(r'^resource-center/$',  resource_center, name="resource_center"),
    url(r'^resource-center/(?P<slug>[\w-]+)/$',  resource_center, name="resource_center"),
    
    url(r'^academic-center/(?P<academic_id>\d+)/$',  academic_center, name="academic_center"),
    url(r'^academic-center/(?P<academic_id>\d+)/(?P<slug>[\w-]+)/$',  academic_center, name="academic_center"),
    
    #Ajax 
    url(r'ajax-ac-state/$',  ajax_ac_state, name='ajax_ac_state'),
    url(r'ajax-ac-location/$',  ajax_ac_location, name='ajax_ac_location'),
    url(r'ajax-ac-pincode/$',  ajax_ac_pincode, name='ajax_ac_pincode'),
    url(r'ajax-district/$',  ajax_district_data, name='ajax_district_data'),
    url(r'ajax-district-collage/$',  ajax_district_collage, name='ajax_district_collage'),
    url(r'ajax-state-collage/$',  ajax_state_collage, name='ajax_state_collage'),
    url(r'ajax-dept-foss/$',  ajax_dept_foss, name='ajax_dept_foss'),
    url(r'ajax-language/$',  ajax_language, name='ajax_language'),
    url(r'ajax_state_details/$',  ajax_state_details, name='ajax_state_details'),
    url(r'ajax-academic-center/$',  ajax_academic_center, name='ajax_academic_center'),
    url(r'ajax-check-foss/$',  ajax_check_foss, name='ajax_check_foss'),
    #url(r'add$',  add_contact', name='add_contact'),
    #url(r'edit/(\d+)$',  edit_contact', name='edit_contact'),   
    #url(r'delete/(\d+)$',  delete_contact', name='delete_contact'),
    # EVENTS V2 URLs
    url(r'^', include('events.urlsv2')),
    url(r'reset-student-password/$',  reset_student_pwd, name='reset_student_pwd'),
    url(r'^ajax-get-schools/$',  get_schools, name='get_schools'),
    url(r'^ajax-get-batches/$',  get_batches, name='get_batches'),
]