from django.shortcuts import render
from creation.models import ContributorRole
from scriptmanager.serializers import ContributorRoleSerializer
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
      # data = 
      # return Response(data=pDatos, status=pStatus, headers={"Access-Control-Allow-Origin":"*"})

  serializer_class = ContributorRoleSerializer

  