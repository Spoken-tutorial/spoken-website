from django.urls import re_path, path, include
from events.views import *
from events.notification import nemail
app_name = 'events'
urlpatterns = [
    path(r'',  events_dashboard, name='events_dashboard'),
    re_path(r'^init/$',  init_events_app, name='init_events_app'),
    
    #cron job
    #todo: test and workshop auto close
    re_path(r'^fix-date-for-first-training/$',  fix_date_for_first_training, name='fix_date_for_first_training'),
    #re_path(r'^training-gentle-reminder/$',  training_gentle_reminder', name='training_gentle_reminder'),
    #re_path(r'^training-completion-reminder/$',  training_completion_reminder', name='training_completion_reminder'),
    re_path(r'^close-predated-ongoing-workshop/$',  close_predated_ongoing_workshop, name='close_predated_ongoing_workshop'),
    re_path(r'^close-predated-ongoing-test/$',  close_predated_ongoing_test, name='close_predated_ongoing_test'),
    
    re_path(r'^test/$', nemail, name='test'),
    
    re_path(r'^ac/$',  ac, name='ac'),
    re_path(r'^ac/new/$',  new_ac, name='new_ac'),
    re_path(r'^ac/(\d+)/edit/$',  edit_ac, name='edit_ac'),
    
    #re_path(r'^xmlparse/$',  xmlparse', name='xmlparse'),
    #re_path(r'^pdf/$',  pdf', name='pdf'),
    re_path(r'^training/permission/$',  training_permission, name='training_permission'),
    re_path(r'^training/accessrole/$',  accessrole, name='training_accessrole'),
    re_path(r'^training/old-training-attendance/$',  old_training_attendance, name='old_training_attendance'),
    re_path(r'^training/old-training-attendance-upload/(\d+)/$',  old_training_attendance_upload, name='old_training_attendance_upload'),
    
    re_path(r'^(?P<role>\w+)/(?P<status>\w+)/$',  organiser_invigilator_index, name='organiser_invigilator_index'),
    re_path(r'^organiser/(?P<status>\w+)/(?P<code>\w+)/(?P<userid>\d+)/$',  rp_organiser, name='rp_organiser'),
    re_path(r'^organiser-handover/$', handover, name='handover'),
    
    re_path(r'^activate-academics/$',  activate_academics, name='activate_academics'),
    re_path(r'^activate-academics-org/(?P<academic_id>\d+)/$',  activate_academic_org, name='activate_academic_org'),

    re_path(r"^accountexecutive/request/(?P<username>[\w. @-]+)/$",  accountexecutive_request, name='accountexecutive_request'),
    re_path(r"^accountexecutive/view/(?P<username>[\w. @-]+)/$",  accountexecutive_view, name='accountexecutive_view'),
    re_path(r"^accountexecutive/(?P<username>[\w. @-]+)/edit/$",  accountexecutive_edit, name='accountexecutive_edit'),
    re_path(r'^accountexecutive/(?P<status>\w+)/(?P<code>\w+)/(?P<userid>\d+)/$',  rp_accountexecutive, name='rp_accountexecutive'),
    
    re_path(r"^organiser/request/(?P<username>[\w. @-]+)/$",  organiser_request, name='organiser_request'),
    re_path(r"^organiser/(?P<username>[\w. @-]+)/edit/$",  organiser_edit, name='organiser_edit'),
    re_path(r"^organiser/view/(?P<username>[\w. @-]+)/$",  organiser_view, name='organiser_view'),

    re_path(r'^invigilator/(?P<status>\w+)/(?P<code>\w+)/(?P<userid>\d+)/$',  rp_invigilator, name='rp_invigilator'),
    re_path(r"^invigilator/request/(?P<username>[\w. @-]+)/$",  invigilator_request, name='invigilator_request'),
    re_path(r"^invigilator/(?P<username>[\w. @-]+)/edit/$",  invigilator_edit, name='invigilator_edit'),
    re_path(r"^invigilator/view/(?P<username>[\w. @-]+)/$",  invigilator_view, name='invigilator_view'),
    
    #live feedback
    re_path(r'^training/live/list/$',  live_training, name='live_training'),
    re_path(r'^training/live/list/(\d+)/$',  live_training, name='live_training'),
    
    re_path(r'^training/subscribe/(\w+)/(\d+)/(\d+)/$',  training_subscribe, name='student_subscribe'),
    re_path(r'^training/(\d+)/attendance/$',  training_attendance, name='training_attend'),
    re_path(r'^training/(\d+)/participant/$',  training_participant, name='training_participant'),
    re_path(r'^training/participant/certificate/(\d+)/(\d+)/$',  training_participant_ceritificate, name='training_participant_ceritificate'),
    re_path(r'^training/participant/feedback/(\d+)/(\d+)/$',  training_participant_feedback, name='training_participant_feedback'),
    
    #live feedback
     re_path(r'^training/participant/lfeedback/(\d+)/(\d+)/$',  training_participant_viewlivefeedback, name='training_participant_viewlivefeedback'),
    re_path(r'^training/participant/lfeedback/(\d+)/$',  training_participant_livefeedback, name='training_participant_livefeedback'),
    
    #language Feedback
    #re_path(r'^training/participant/language-feedback/(\d+)/(\d+)/$',  training_participant_view_language_feedback', name='training_participant_viewlivefeedback'),
    re_path(r'^training/participant/language-feedback/(\d+)/(\d+)/$',  training_participant_language_feedback, name='training_participant_language_feedback'),
    
    re_path(r'^training/(?P<role>\w+)/request/$',  training_request, name='training_request'),
    re_path(r'^training/(?P<role>\w+)/clone/$',  training_clone, name='training_clone'),
    re_path(r'^training/(?P<role>\w+)/(?P<rid>\d+)/approvel/$',  training_approvel, name='training_approvel'),
    re_path(r'^training/(?P<role>\w+)/(?P<status>\w+)/$',  training_list, name='training_list'),
    re_path(r'^training/(?P<role>\w+)/(?P<rid>\d+)/edit/$',  training_request, name='training_edit'),
    re_path(r'^training/(?P<role>\w+)/(?P<rid>\d+)/clone/$',  training_clone, name='training_clone'),
    #re_path(r'^training/training-completion/(?P<rid>\d+)/$',  training_completion', name="training_completion"),
    re_path(r'^training/view/training-completion/(?P<rid>\d+)/$',  view_training_completion, name="view_training_completion"),
    
    #re_path(r'^test/subscribe/(\d+)/(\d+)/$',  test_student_subscribe', name='test_student_subscribe'),
    re_path(r'^test/(\d+)/participant/$',  test_participant, name='test_participant'),
    re_path(r'^test/participant/certificate/(\d+)/(\d+)/$',  test_participant_ceritificate, name='test_participant_ceritificate'),
    re_path(r'^test/participant/certificate/all/(\d+)/$',  test_participant_ceritificate_all, name='test_participant_ceritificate_all'),
    re_path(r'^test/(\d+)/attendance/$',  test_attendance, name='test_attendance'),
    re_path(r'^test/(?P<role>\w+)/request/$',  test_request, name='test_request'),
    re_path(r'^test/(?P<role>\w+)/(?P<rid>\d+)/approvel/$',  test_approvel, name='test_approvel'),
    re_path(r'^test/(?P<role>\w+)/(?P<status>\w+)/$',  test_list, name='test_list'),
    re_path(r'^test/(?P<role>\w+)/(?P<rid>\d+)/edit/$',  test_request, name='test_request'),
    re_path(r'^test/verify-test-certificate/$', verify_test_certificate, name='verify_test_certificate'),

    re_path(r'^delete-notification/(\w+)/(\d+)/$',  delete_events_notification, name="delete_events_notification"),
    re_path(r'^clear-notifications/(\w+)/$',  clear_events_notification, name="clear_events_notification"),
    
    re_path(r'^resource-center/$',  resource_center, name="resource_center"),
    re_path(r'^resource-center/(?P<slug>[\w-]+)/$',  resource_center, name="resource_center"),
    
    re_path(r'^academic-center/(?P<academic_id>\d+)/$',  academic_center, name="academic_center"),
    re_path(r'^academic-center/(?P<academic_id>\d+)/(?P<slug>[\w-]+)/$',  academic_center, name="academic_center"),
    
    #Ajax 
    re_path(r'ajax-ac-state/$',  ajax_ac_state, name='ajax_ac_state'),
    re_path(r'ajax-ac-location/$',  ajax_ac_location, name='ajax_ac_location'),
    re_path(r'ajax-ac-pincode/$',  ajax_ac_pincode, name='ajax_ac_pincode'),
    re_path(r'ajax-district/$',  ajax_district_data, name='ajax_district_data'),
    re_path(r'ajax-district-collage/$',  ajax_district_collage, name='ajax_district_collage'),
    re_path(r'ajax-state-collage/$',  ajax_state_collage, name='ajax_state_collage'),
    re_path(r'ajax-dept-foss/$',  ajax_dept_foss, name='ajax_dept_foss'),
    re_path(r'ajax-language/$',  ajax_language, name='ajax_language'),
    re_path(r'ajax_state_details/$',  ajax_state_details, name='ajax_state_details'),
    re_path(r'ajax-academic-center/$',  ajax_academic_center, name='ajax_academic_center'),
    re_path(r'ajax-check-foss/$',  ajax_check_foss, name='ajax_check_foss'),
    #re_path(r'add$',  add_contact', name='add_contact'),
    #re_path(r'edit/(\d+)$',  edit_contact', name='edit_contact'),   
    #re_path(r'delete/(\d+)$',  delete_contact', name='delete_contact'),
    # EVENTS V2 URLs
    path(r'', include('events.urlsv2')),
    re_path(r'reset-student-password/$',  reset_student_pwd, name='reset_student_pwd'),
    re_path(r'^ajax-get-schools/$',  get_schools, name='get_schools'),
    re_path(r'^ajax-get-batches/$',  get_batches, name='get_batches'),
]