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
    # url(
    #   r'^list_events', 
    #   TrainingEventsListView.as_view(template_name="list_events.html"), 
    #   name="list_events"
    # ),
    url(
      r'^list_events/(?P<status>\w+)/$', 
      TrainingEventsListView.as_view(template_name="list_events.html"), 
      name="list_events"
    ),
    url(
      r'^register_user', register_user, name="register_user"),
    url(
      r'^reg_success', reg_success, name="reg_success"),
    url(
      r'^(?P<eventid>\d+)/participants$', 
      EventPraticipantsListView.as_view(template_name="list_event_participants.html"), 
      name="list_event_participants"
    ),
    ]
