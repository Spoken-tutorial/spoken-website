from django.conf.urls import url
from . import views

# To use the API document generator for the script creation system 
# (a) add 'rest_framework_swagger' to INSTALLED_APPS in spoken/settings.py
# (b) uncomment the api/docs url in the urlpatterns given below
# (c) uncomment the following two lines
# from rest_framework_swagger.views import get_swagger_view
# schema_view = get_swagger_view(title='Spoken Tutorial\'s API')

urlpatterns = [
  url(r'api/foss/(?P<fid>[0-9]+)/language/(?P<lid>[0-9]+)/tutorials/$', views.TutorialDetailList.as_view()), 
  url(r'api/foss/$', views.ContributorRoleList.as_view()), 
  url(r'api/tutorial/(?P<tid>[0-9]+)/language/(?P<lid>[0-9]+)/scripts/(?P<vid>[0-9]+)/$', views.ScriptCreateAPIView.as_view()),
  url(r'api/tutorial/(?P<tid>[0-9]+)/language/(?P<lid>[0-9]+)/scripts/(?P<vid>[0-9]+)/(?P<script_detail_id>[0-9]+)/$', views.ScriptDetailAPIView.as_view()),
  url(r'api/scripts/(?P<script_detail_id>[0-9]+)/comments/$', views.CommentCreateAPIView.as_view()),
  url(r'api/scripts/(?P<script_detail_id>[0-9]+)/reversions/$', views.ReversionListView.as_view()),
  url(r'api/scripts/(?P<script_detail_id>[0-9]+)/reversions/(?P<reversion_id>[0-9]+)/$', views.ReversionRevertView.as_view()),
  url(r'api/scripts/(?P<script_id>[0-9]+)/$', views.RelativeOrderingAPI.as_view()),
  url(r'api/scripts/published/$', views.PublishedScriptAPI.as_view()),
  url(r'api/scripts/review/$', views.ForReviewScriptAPI.as_view()),
  url(r'api/comments/(?P<comment_id>[0-9]+)/$', views.CommentAPI.as_view()),
  # url(r'api/docs/$', schema_view),
  url(r'', views.index, name='home')
]