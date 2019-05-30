from django.shortcuts import render
from creation.models import ContributorRole
from scriptmanager.serializers import ContributorRoleSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

def index(request):
  # print 'here'
  return render(request, 'scriptmanager/index.html')

class ContributorRoleList(generics.ListCreateAPIView):
  def get_queryset(self):
      return ContributorRole.objects.filter(user=self.request.user)
      # data = 
      # return Response(data=pDatos, status=pStatus, headers={"Access-Control-Allow-Origin":"*"})

  serializer_class = ContributorRoleSerializer

  