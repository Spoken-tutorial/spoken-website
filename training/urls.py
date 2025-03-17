#training urls
from django.urls import re_path
from training.views import *

app_name = 'training'
urlpatterns = [
    re_path(
      r'^$', 
      TrainingEventCreateView.as_view(template_name="create_event.html"), 
      name="create_event"
    ),
    re_path(
      r'^list_events/(?P<status>\w+)/$', 
      TrainingEventsListView.as_view(template_name="list_events.html"), 
      name="list_events"
    ),
    re_path(
      r'^register_user/$', register_user, name="register_user"),
    re_path(
      r'^reg_success/(?P<user_type>\w+)/$', reg_success, name="reg_success"),
    # re_path(
    #   r'^(?P<eventid>\d+)/participants$', 
    #   EventPraticipantsListView.as_view(template_name="list_event_participants.html"), 
    #   name="list_event_participants"
    # ),
    re_path(
      r'^(?P<pk>\d+)/update$', 
      EventUpdateView.as_view(template_name="edit_event.html"), 
      name="edit_event"
    ),
    re_path(
      r'^(?P<pk>\d+)/approve', approve_event_registration, name="approve_event_registration"),
    re_path(
      r'^(?P<pk>\d+)/close_event', close_event, name="close_event"),
    re_path(
      r'^event/(?P<role>\w+)/(?P<status>\w+)/$',
      listevents, 
      name='tr_event_list'
    ),
    re_path(
      r'^(?P<eventid>\d+)/upload_participants$', 
      ParticipantCreateView.as_view(template_name="upload_participants.html"), 
      name="upload_participants"
    ),
    re_path(
      r'^(?P<eventid>\d+)/participants$', 
      EventAttendanceListView.as_view(template_name="list_event_participants.html"), 
      name="event_attendance"
    ),
    re_path(r'^ajax_check_college/', ajax_check_college, name="ajax_check_college"),
    re_path(r'^upload_college_details/', upload_college_details, name="upload_college_details"),
    re_path(
      r'^generate_training_certificate/$', 
      EventTrainingCertificateView.as_view(), \
        name="generate_training_certificate"
        ),
    # re_path(r'^participant-transactions/$', participant_transactions,name="participant_transactions"),
    # re_path(
    #   r'^participant-transactions/$', 
    #   ParticipantTransactionsListView.as_view(template_name="participant_transaction_list.html"), 
    #   name="participant_transaction_list"
    # ),
    re_path(r'ajax-collage-event/$',  ajax_collage_event, name='ajax_collage_event'),
    re_path(
      r'^participant-transactions/(?P<purpose>\w+)/$',
      participant_transactions, 
      name='participant_transactions'
    ),
    re_path(r'transaction_csv/(?P<purpose>\w+)/$', transaction_csv, name='transaction_csv'),
    re_path(r'reopen-event/(?P<eventid>\w+)/$', reopen_event, name='reopen_event'),
    re_path(
      r'^(?P<eventid>\d+)/eventparticipants$', 
      EventParticipantsListView.as_view(template_name="stat_event_participants.html"), 
      name="event_participants"
    ),
    re_path(r'^ajax_add_teststatus/', ajax_add_teststatus, name="ajax_add_teststatus"),
    re_path(
      r'^generate_test_certificate/(?P<testfossid>\d+)/$', 
      EventTestCertificateView.as_view(), \
        name="generate_test_certificate"
        ),
    re_path(r'^verify-ilwtest-certificate/$', verify_ilwtest_certificate, name='verify_ilwtest_certificate'),
    re_path(r'^companies/new/$', add_company, name='add_company'),
    re_path(r'^companies/$', list_companies, name='list_companies'),
    re_path(r'^edit_company/(\d+)/$', edit_company, name='edit_company'),
    ]
