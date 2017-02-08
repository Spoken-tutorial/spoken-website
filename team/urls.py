from django.conf.urls import url
from .views import TeamListView

urlpatterns = [
    url(r'^(?P<role>[-\w ]+)/$', TeamListView.as_view(template_name="team_members.html"), name="team"),
]
