# urls.py
from django.conf.urls import url
from team.views import *
urlpatterns = [
  url(
    r'^(?P<role>[-\w]+)/$',
    TeamListView.as_view(template_name="team_members.html"),
    name="team"
  ),
]
