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
      r'^list_events', 
      TrainingEventsListView.as_view(template_name="list_events.html"), 
      name="list_events"
    ),
    url(
      r'^register_user',
      RegisterUserView.as_view(template_name="register_user.html"))
    ]