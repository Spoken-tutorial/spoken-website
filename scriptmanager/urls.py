from django.conf.urls import url
from . import views
urlpatterns = [
  url(r'^$', views.index, name='home'),
  url(r'api/foss/', views.ContributorRoleList.as_view()), 
  url(r'api/tutoriallist/', views.TutorialsList.as_view()), 
  url(r'api/tutorials/', views.TutorialDetails.as_view()), 
  url(r'api/scripts/', views.ScriptsList.as_view()),
  # url(r'^api/scripts/(?P<fossid>[0-9]+)/', views.ScriptsList()
]
