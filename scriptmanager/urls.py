from django.conf.urls import url
from . import views
urlpatterns = [
  url(r'^$', views.index, name='home'),
  url(r'api/foss/', views.ContributorRoleList.as_view()),
  url(r'api/tutorials/', views.TutorialsList.as_view())
]