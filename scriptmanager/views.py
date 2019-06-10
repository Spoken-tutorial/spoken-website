from django.shortcuts import render
from creation.models import ContributorRole,TutorialDetail,User
from .models import Scripts,ScriptDetails
from .serializers import ContributorRoleSerializer,TutorialDetailSerializer,ScriptsDetailSerializer,ScriptsSerializer
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


class ContributorRoleList(generics.ListAPIView):
  def get_queryset(self):
      return ContributorRole.objects.filter(user=self.request.user)
  serializer_class = ContributorRoleSerializer


class TutorialDetailList(generics.ListAPIView):
  serializer_class=TutorialDetailSerializer
    
  def get_queryset(self):
    if (self.kwargs.get('fid') == 'all'):
      return TutorialDetail.objects.all().order_by('order')
      
    return TutorialDetail.objects.filter(foss=self.kwargs.get('fid')).order_by('order')




class ScriptCreateAPIView(generics.ListCreateAPIView):
  serializer_class=ScriptsDetailSerializer

  def get_queryset(self):
    user=User.objects.filter(username=self.request.user)
    script_pk=Scripts.objects.filter(tutorial_id=int(self.kwargs['tid']),user=user[0].id)
    return ScriptDetails.objects.filter(script=script_pk)
   
  def post(self, request,tid):
    serializer_class=ScriptsSerializer
    data=request.data.pop('details')
    try:
      script= Scripts.objects.create(tutorial_id=int(self.kwargs['tid']),user=self.request.user)
      for x in data:
        script_details = ScriptDetails.objects.create(script=script,**x)
      return Response({'status': True})
    except:
      return Response({'status': False})


   