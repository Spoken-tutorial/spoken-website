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
      return TutorialDetail.objects.filter(user=self.request.user).order_by('order')
      
    return TutorialDetail.objects.filter(user=self.request.user,foss=self.kwargs.get('fid')).order_by('order')


# class ScriptCreateAPIView(generics.ListCreateAPIView):
#   serializer_class=ScriptsDetailSerializer

#   def get_queryset(self): 
#     user=User.objects.filter(username=self.request.user)
#     script_pk=Scripts.objects.filter(tutorial_id=int(self.kwargs['tid']),user=user[0].id)
#     return ScriptDetails.objects.filter(script=script_pk)
      
#   def create(self, request,tid):
#     details=request.data.pop('data')
#     # for x in details:
#     #   script_details = ScriptDetails.objects.create(script=script,**x)
#     try:
#       model=TutorialDetail.objects.get(pk=int(self.kwargs['tid']))
#       serializer = TutorialDetailSerializer(model,data={"script_status":1}, partial=True)
#       if serializer.is_valid():
#           serializer.save()

#       script= Scripts.objects.create(tutorial_id=int(self.kwargs['tid']),user=self.request.user)
#       for item in details:
#         item.update( {"script":script.pk})
#       serialized=ScriptsDetailSerializer(data=details,many=True)
#       if serialized.is_valid():
#         serialized.save()
#         return Response({'status': True},status=201)
#     except:
#         return Response({'status': False},status=400) 

#   def patch(self,request, tid):
#     delete_data = request.data.pop('delete')
#     update_data = request.data.pop('update')
#     insert_data = request.data.pop('insert')
#     try:
#       script = Scripts.objects.get(tutorial_id=int(self.kwargs['tid']),user=self.request.user)

#       serialized = ScriptsDetailSerializer(data=insert_data,many=True)
#       if serialized.is_valid():
#         serialized.save()

#       for key in delete_data:
#         ScriptDetails.objects.get(pk=key,script_id=script.pk).delete()


#       for script_details in update_data:
#         script=ScriptDetails.objects.get(pk=script_details['id'])
#         serializer = ScriptsDetailSerializer(script, data=script_details)
#         if serializer.is_valid():
#           serializer.save()
#       return Response({'status': True},status=201)
#     except:
#       return Response({'status': False},status=400) 


class ScriptCreateAPIView(generics.ListCreateAPIView):
  serializer_class=ScriptsDetailSerializer

  def get_queryset(self): 
    user=User.objects.filter(username=self.request.user)
    script_pk=Scripts.objects.filter(tutorial_id=int(self.kwargs['tid']),user=user[0].id)
    return ScriptDetails.objects.filter(script=script_pk)
      
  def create(self, request,tid):
    details=request.data['data']
    # for x in details:
    #   script_details = ScriptDetails.objects.create(script=script,**x)
    try:
      try:
        script = Scripts.objects.create(tutorial_id=int(self.kwargs['tid']),user=self.request.user)
        model=TutorialDetail.objects.get(pk=int(self.kwargs['tid']))
        serializer = TutorialDetailSerializer(model,data={"script_status":1}, partial=True)
        if serializer.is_valid():
          serializer.save()
      except:
        script = Scripts.objects.get(tutorial_id=int(self.kwargs['tid']),user=self.request.user)
        
      for item in details:
        item.update( {"script":script.pk})
      serialized = ScriptsDetailSerializer(data = details,many = True) #inserting a details array without iterating
      if serialized.is_valid():
        serialized.save()
        return Response({'status': True},status=201)
      return Response({'status': False},status=400) 
    except:
        return Response({'status': False},status=400) 

  def patch(self,request, tid):
    try:
      script_data = Scripts.objects.get(tutorial_id=int(self.kwargs['tid']),user=self.request.user)
      script_details = self.request.data
      script = ScriptDetails.objects.get(pk=(script_details['id']))
      serializer = ScriptsDetailSerializer(script, data=script_details)
      if serializer.is_valid():
        serializer.save()
      return Response({'status': True},status=200)
    except:
      return Response({'status': False},status=400) 

  def delete(self,request,tid):
    data=request.data.pop('delete')
    try:
      script = Scripts.objects.get(tutorial_id=int(self.kwargs['tid']),user=self.request.user)
      for key in data:
        ScriptDetails.objects.get(pk=key,script_id=script.pk).delete()
      return Response({'status': True},status=202) 
    except:
      return Response({'status': False},status=400) 


