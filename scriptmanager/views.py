from django.shortcuts import render
from creation.models import ContributorRole,TutorialDetail,User,Language
from .models import Scripts,ScriptDetails,Comments
from .serializers import ContributorRoleSerializer,TutorialDetailSerializer,ScriptsDetailSerializer,ScriptsSerializer,CommentsSerializer,ReversionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework_jwt.settings import api_settings
from reversion.models import Version
import os
from django.core.files.storage import FileSystemStorage
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import time

def index(request):
  jwt_payload_handler  =  api_settings.JWT_PAYLOAD_HANDLER
  jwt_encode_handler  =  api_settings.JWT_ENCODE_HANDLER
  payload  =  jwt_payload_handler(request.user)
  token  =  jwt_encode_handler(payload) 
  return render(request, 'scriptmanager/index.html', {'token': token})


class ContributorRoleList(generics.ListAPIView):
  def get_queryset(self):
      return ContributorRole.objects.filter(user = self.request.user,status = True)
  serializer_class  =  ContributorRoleSerializer


class TutorialDetailList(generics.ListAPIView):
  serializer_class = TutorialDetailSerializer

  def get_serializer_context(self):
    return {"lang": self.kwargs['lid'],"user":self.request.user}
    
  def get_queryset(self):
    if ContributorRole.objects.filter(user  =  self.request.user,foss_category  =  self.kwargs.get('fid'), language=self.kwargs.get('lid')).exists():
      return TutorialDetail.objects.filter(foss  =  self.kwargs.get('fid')).order_by('order')
    else:
      return None

class ScriptCreateAPIView(generics.ListCreateAPIView):
  serializer_class = ScriptsDetailSerializer

  def getUlData(self,data):
    data=str(data).replace("<li></li>","")
    soup=BeautifulSoup(data,'html.parser')
    if soup.find_all('ul'):
      all_data=soup.find_all('ul')
      for data in all_data:
        for p in data.find_all('p'):
          p.name='li'
          
    if soup.find_all('ol'):
      all_data=soup.find_all('ol')
      for data in all_data: 
        for p in data.find_all('p'):
          p.name='li'
    return str(soup)


  def scriptsData(self, html,script):
    soup=BeautifulSoup(html,'html.parser')
    table=soup.find("table") 
    # print(table)
    if(table.find("tbody")):
      table=table.find("tbody")
    details=[]
    count=0
    for row in table.find_all('tr'):
      count+=1
      if row.find_all("th"):
        columns = row.find_all('th')
      elif row.find_all('td'):  
        columns = row.find_all('td')
      try:
        details.append({"order": count,"cue": self.getUlData(columns[0]),"narration": self.getUlData(columns[1]),"script":script.pk})
      except:
        continue
    details.pop(0)
    return details

  def get_queryset(self): 
    tutorial=TutorialDetail.objects.get(pk = int(self.kwargs['tid']))
    language=Language.objects.get(pk = int(self.kwargs['lid']))
    script = Scripts.objects.get(tutorial = tutorial,language = language,user=self.request.user)
    return ScriptDetails.objects.filter(script = script)

  def create(self, request,tid,lid):
    details=[]
    type=request.data['type']

    try:
      tutorial=TutorialDetail.objects.get(pk = int(self.kwargs['tid']))
      language=Language.objects.get(pk = int(self.kwargs['lid']))
      if not  Scripts.objects.filter(user = self.request.user,tutorial = tutorial,language = language).exists():
        script = Scripts.objects.create(tutorial = tutorial,language = language, user = self.request.user)
      else:
        script = Scripts.objects.get(tutorial = tutorial,language = language, user = self.request.user)

      if(type=='form'):
        details = request.data['details']
        for item in details:
          item.update( {"script":script.pk})

      elif(type=='file'):
        myfile=request.FILES['docs']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        doc_file=os.getcwd()+'/media/'+filename
        os.system('libreoffice --convert-to html '+doc_file)
        html_file=os.path.splitext(os.getcwd()+'/'+filename)[0]+'.html'
        run_time=0
        html=0
        while run_time < 3.0:
          try:
            html = open(html_file,'r')
            break
          except:
            time.sleep(.4)
            run_time+=.4
        html = open(html_file,'r')
        details=self.scriptsData(html,script)
        os.system('rm '+ doc_file + ' '+html_file)
      
      elif (type=="template"):
        data=request.data['details']
        details=self.scriptsData(data,script)

      serialized  =  ScriptsDetailSerializer(data  =  details,many  =  True) #inserting a details array without iterating
      if serialized.is_valid():
        serialized.save()
        return Response({'status': True},status = 201)
    except:
      if type=='file':
        os.system('rm '+ doc_file + ' '+html_file)
      return Response({'status': False},status = 400) 



  def patch(self,request,tid,lid):
    try:
      tutorial=TutorialDetail.objects.get(pk = int(self.kwargs['tid']))
      language=Language.objects.get(pk = int(self.kwargs['lid']))
      Scripts.objects.get(tutorial = tutorial, language = language, user = self.request.user)

      script_details  =  self.request.data
      script  =  ScriptDetails.objects.get(pk = (script_details['id']))
      serializer  =  ScriptsDetailSerializer(script, data = script_details)
      if serializer.is_valid():
        serializer.save()
      return Response({'status': True},status = 200)
    except:
      return Response({'status': False},status = 400) 


  def delete(self,request,tid,lid,script_detail_id):
    try:
      tutorial=TutorialDetail.objects.get(pk = int(self.kwargs['tid']))
      language=Language.objects.get(pk = int(self.kwargs['lid']))
      script = Scripts.objects.get(tutorial = tutorial, language = language, user = self.request.user)

      ScriptDetails.objects.get(pk = int(self.kwargs['script_detail_id']),script = script).delete()
      if not ScriptDetails.objects.filter(script_id = script.pk).exists(): 
       script.delete()
      return Response({'status': True},status = 202) 
    except:
      return Response({'status': False},status = 400) 


class CommentCreateAPIView(generics.ListCreateAPIView):
  serializer_class=CommentsSerializer

  def get_queryset(self):
    try:
      script_detail=ScriptDetails.objects.get(pk=int(self.kwargs['script_detail_id']))
      return Comments.objects.filter(script_details = script_detail).order_by('created')
    except:
      return None


  def create(self,request,script_detail_id):
    try:
      script_data=ScriptDetails.objects.get(pk=script_detail_id)
      Comments.objects.create(comment=request.data['comment'],user=self.request.user,script_details=script_data)
      return Response({'status': True},status = 202)
    except:
      return Response({'status': False},status = 400)


class ReversionListView(generics.ListAPIView):
  serializer_class = ReversionSerializer

  def get_queryset(self):
    try:
      script_detail=ScriptDetails.objects.get(pk=int(self.kwargs['script_detail_id']))
      reversion_data = Version.objects.get_for_object(script_detail)
      data = []
      count=0
      for i in reversion_data:
        count+=1
        result=i.field_dict
        rev_time=i.revision.date_created+timedelta(hours=5,minutes=30)
        result.update({"reversion_id": count,"date_time":rev_time.strftime("%Y-%m-%d %I:%M %p"),"user":i.revision.user})
        data.append(result)
      return ReversionSerializer(data,many=True).data
    except:
      return None

  def patch(self,request,script_detail_id):
    try:
      script_detail=ScriptDetails.objects.get(pk=int(self.kwargs['script_detail_id']))
      reversion_data = Version.objects.get_for_object(script_detail)
      reversion_data[request.data['reversion_id']-1].revision.revert()
      return Response({'status': True},status = 201)
    except:
      return Response({'status': False},status = 400)
