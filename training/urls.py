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
      r'^register_user', register_user, name="register_user"),
    url(
      r'^reg_success/(?P<user_type>\w+)/$', reg_success, name="reg_success"),
    url(
      r'^(?P<eventid>\d+)/participants$', 
      EventPraticipantsListView.as_view(template_name="list_event_participants.html"), 
      name="list_event_participants"
    ),
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
    ]
