from django.conf.urls import url
from . import views

urlpatterns = [
  url(r'api/foss/(?P<fid>[0-9a-z]+)/tutorials/$', views.TutorialDetailList.as_view()), 
  url(r'api/foss/$', views.ContributorRoleList.as_view()), 
  url(r'api/tutorial/(?P<tid>[0-9]+)/scripts/$', views.ScriptCreateAPIView.as_view()),
  url(r'api/tutorial/(?P<tid>[0-9]+)/scripts/(?P<script_detail_pk>[0-9]+)/$', views.ScriptCreateAPIView.as_view()),
  url(r'', views.index, name='home'),
]
