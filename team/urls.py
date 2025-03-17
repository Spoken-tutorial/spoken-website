# Third Party Stuff
from django.urls import re_path

from .views import TeamListView
app_name = 'team'
urlpatterns = [
    re_path(r'^(?P<role>[-\w ]+)/$', TeamListView.as_view(template_name="team_members.html"), name="team"),
]
