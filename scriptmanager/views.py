from django.shortcuts import render
from creation.models import ContributorRole,TutorialDetail
from .models import Scripts
from .serializers import ContributorRoleSerializer,TutorialDetailSerializer,ScriptsPostSerializer,  ScriptsGetSerializer,ScriptsDetailSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework_jwt.settings import api_settings

def index(request):
  jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
  jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

  payload = jwt_payload_handler(request.user)
  token = jwt_encode_handler(payload) 
   
  return render(request, 'scriptmanager/index.html', {'token': token})

class ContributorRoleList(generics.ListCreateAPIView):
  def get_queryset(self):
      return ContributorRole.objects.filter(user=self.request.user)
  serializer_class = ContributorRoleSerializer



class TutorialDetails(generics.ListCreateAPIView):
  serializer_class=TutorialDetailSerializer
    
  def get_queryset(self):
    fid=self.request.query_params.get('fid')
    if fid is None:
          return TutorialDetail.objects.filter(user=self.request.user).order_by('order')
    return TutorialDetail.objects.filter(foss_id=self.request.query_params.get('fid'),user=self.request.user).order_by('order')

class ScriptsList(generics.ListCreateAPIView):
  queryset = Scripts.objects.all()

  def get_serializer_class(self):
    if self.request.method == 'POST':
        return ScriptsPostSerializer
    return ScriptsGetSerializer



