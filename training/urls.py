#training urls
from django.conf.urls import url
from training.views import *

app_name = 'training'
urlpatterns = [
    url(
      r'^$', 
      TrainingEventCreateView.as_view(template_name="create_event.html"), 
      name="create_event"
    ),
    url(
      r'^list_events/(?P<status>\w+)/$', 
      TrainingEventsListView.as_view(template_name="list_events.html"), 
      name="list_events"
    ),
    url(
      r'^register_user/$', register_user, name="register_user"),
    url(
      r'^reg_success/(?P<user_type>\w+)/$', reg_success, name="reg_success"),
    # url(
    #   r'^(?P<eventid>\d+)/participants$', 
    #   EventPraticipantsListView.as_view(template_name="list_event_participants.html"), 
    #   name="list_event_participants"
    # ),
    url(
      r'^(?P<pk>\d+)/update$', 
      EventUpdateView.as_view(template_name="edit_event.html"), 
      name="edit_event"
    ),
    url(
      r'^(?P<pk>\d+)/approve', approve_event_registration, name="approve_event_registration"),
    url(
      r'^(?P<pk>\d+)/close_event', close_event, name="close_event"),
    url(
      r'^event/(?P<role>\w+)/(?P<status>\w+)/$',
      listevents, 
      name='tr_event_list'
    ),
    url(
      r'^(?P<eventid>\d+)/upload_participants$', 
      ParticipantCreateView.as_view(template_name="upload_participants.html"), 
      name="upload_participants"
    ),
    url(
      r'^(?P<eventid>\d+)/participants$', 
      EventAttendanceListView.as_view(template_name="list_event_participants.html"), 
      name="event_attendance"
    ),
    url(r'^ajax_check_college/', ajax_check_college, name="ajax_check_college"),
    url(r'^upload_college_details/', upload_college_details, name="upload_college_details"),
    url(
      r'^generate_training_certificate/$', 
      EventTrainingCertificateView.as_view(), \
        name="generate_training_certificate"
        ),
    # url(r'^participant-transactions/$', participant_transactions,name="participant_transactions"),
    # url(
    #   r'^participant-transactions/$', 
    #   ParticipantTransactionsListView.as_view(template_name="participant_transaction_list.html"), 
    #   name="participant_transaction_list"
    # ),
    url(r'ajax-collage-event/$',  ajax_collage_event, name='ajax_collage_event'),
    url(
      r'^participant-transactions/(?P<purpose>\w+)/$',
      participant_transactions, 
      name='participant_transactions'
    ),
    url(r'transaction_csv/(?P<purpose>\w+)/$', transaction_csv, name='transaction_csv'),
    url(r'reopen-event/(?P<eventid>\w+)/$', reopen_event, name='reopen_event'),
    url(
      r'^(?P<eventid>\d+)/eventparticipants$', 
      EventParticipantsListView.as_view(template_name="stat_event_participants.html"), 
      name="event_participants"
    ),
    url(r'^ajax_add_teststatus/', ajax_add_teststatus, name="ajax_add_teststatus"),
    url(
      r'^generate_test_certificate/(?P<testfossid>\d+)/$', 
      EventTestCertificateView.as_view(), \
        name="generate_test_certificate"
        ),
    url(r'^verify-ilwtest-certificate/$', verify_ilwtest_certificate, name='verify_ilwtest_certificate'),
    ]
