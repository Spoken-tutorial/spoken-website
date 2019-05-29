# Third Party Stuff
from django.conf.urls import url

from .views import TeamListView
app_name = 'team'
urlpatterns = [
    url(r'^(?P<role>[-\w ]+)/$', TeamListView.as_view(template_name="team_members.html"), name="team"),
]
