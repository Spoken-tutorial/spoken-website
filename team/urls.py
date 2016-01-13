# urls.py
from django.conf.urls import url
from team.views import *
urlpatterns = [
  url(
    r'^contributor/$',
    TeamContributorListView.as_view(template_name="team_members.html"),
    name="team-contributor"
  ),
  url(
    r'^domain-reviewer/$',
    TeamDomainListView.as_view(template_name="team_members.html"),
    name="team-Domain"
  ),
]
