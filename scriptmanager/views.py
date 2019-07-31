from django.shortcuts import render, redirect
from creation.models import ContributorRole,TutorialDetail,User,Language
from .models import Scripts,ScriptDetails,Comments
from .serializers import ContributorRoleSerializer,TutorialDetailSerializer,ScriptsDetailSerializer,ScriptsSerializer,CommentsSerializer,ReversionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler as default_jwt_payload_handler
from reversion.models import Version
import os
from django.core.files.storage import FileSystemStorage
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
import time
from creation.views import is_videoreviewer,is_domainreviewer,is_qualityreviewer
import uuid
import subprocess 

def custom_jwt_payload_handler(user):
  payload = default_jwt_payload_handler(user)

  payload['is_videoreviewer'] = is_videoreviewer(user)
  payload['is_domainreviewer'] = is_domainreviewer(user)
  payload['is_qualityreviewer'] = is_qualityreviewer(user)

  return payload

def index(request):
  if request.user.is_authenticated:
    jwt_payload_handler  =  api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler  =  api_settings.JWT_ENCODE_HANDLER
    payload  =  jwt_payload_handler(request.user)
    token  =  jwt_encode_handler(payload) 
    return render(request, 'scriptmanager/index.html', {'token': token})
  return redirect('home')


class ContributorRoleList(generics.ListAPIView):
  def get_queryset(self):
      return ContributorRole.objects.filter(user = self.request.user,status = True)

  def get(self, request):
    categories = ContributorRoleSerializer(self.get_queryset(), many=True).data

    unique_categories = {}
    res = []

    for category in categories:
      category_id = category['foss_category']['id']

      if category_id not in unique_categories:
        foss_category = category['foss_category']
        unique_categories[category_id] = {
          'foss_category': {
            'id': foss_category['id'],
            'name': foss_category['name'],
            'description': foss_category['description']
          },
          'languages': []
        }

      unique_categories[category_id]['languages'].append(category['language'])

    for (k,v) in unique_categories.items():
      res.append(v)

    return Response({ 'data': res }, status=200)

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
    try:
      tutorial=TutorialDetail.objects.get(pk = int(self.kwargs['tid']))
      language=Language.objects.get(pk = int(self.kwargs['lid']))
      script = Scripts.objects.get(tutorial = tutorial,language = language)
      user=self.request.user
      if is_domainreviewer(user) or is_qualityreviewer(user) or is_videoreviewer(user) or script.user == user or script.status == True:
        script_details = ScriptDetails.objects.filter(script = script)
        ordering = script.ordering

        if (len(ordering) == 0):
          return script_details

        ordering = ordering.split(',')
        ordering = list(map(int, ordering))
        script_details = sorted(script_details, key=lambda s: ordering.index(s.pk))
        
        return script_details
    except:
      return None

  def create(self, request,tid,lid):
    details=[]
    create_request_type=request.data['type']

    tutorial=TutorialDetail.objects.get(pk = int(self.kwargs['tid']))
    language=Language.objects.get(pk = int(self.kwargs['lid']))
    if not  Scripts.objects.filter(user = self.request.user,tutorial = tutorial,language = language).exists():
      script = Scripts.objects.create(tutorial = tutorial,language = language, user = self.request.user)
    else:
      script = Scripts.objects.get(tutorial = tutorial,language = language, user = self.request.user)

    if(create_request_type=='form'):
      details = request.data['details']
      for item in details:
        item.update( {"script":script.pk})
    elif(create_request_type=='file'):
      myfile=request.FILES['docs']
      fs = FileSystemStorage()
      uid=uuid.uuid4().hex
      filename = fs.save(uid, myfile)
      doc_file=os.getcwd()+'/media/'+filename
      #os.system('libreoffice --convert-to html '+doc_file)
      if subprocess.check_call('soffice --convert-to html '+doc_file+' --outdir media', shell=True) ==0:
        html_file= 'media/'+uid+".html"

        with open(html_file,'r') as html:
          details=self.scriptsData(html,script)
        os.system('rm '+ doc_file + ' '+html_file)
      else:
        return Response({'status': False},status = 400)

    elif (create_request_type=="template"):
      data=request.data['details']
      details=self.scriptsData(data,script)

    serialized  =  ScriptsDetailSerializer(data  =  details,many  =  True) #inserting a details array without iterating
    if serialized.is_valid():
      serialized.save()
      
      if (create_request_type == 'form'):
        ordering = request.data['ordering']
        
        for slide in serialized.data:
          ordering = ordering.replace('-1', str(slide.get('id')), 1)
        
        script.ordering = ordering
        script.save()

      return Response({'status': True, 'data': serialized.data },status = 201)
    return Response({'status': False},status = 400)

  def patch(self, request,tid,lid):
    try:
      tutorial=TutorialDetail.objects.get(pk = int(self.kwargs['tid']))
      language=Language.objects.get(pk = int(self.kwargs['lid']))
      script = Scripts.objects.get(user = self.request.user,tutorial = tutorial,language = language)
      script.status=True
      script.save()
      return Response({'status': True},status = 200) 
    except:
      return Response({'status': False},status = 400) 

class ScriptAPIView(generics.ListAPIView):
  def patch(self,request,tid,lid,script_detail_id):
    try:
      tutorial=TutorialDetail.objects.get(pk = int(self.kwargs['tid']))
      language=Language.objects.get(pk = int(self.kwargs['lid']))
      Scripts.objects.get(tutorial = tutorial, language = language, user = self.request.user)

      script_details  =  self.request.data
      script_details['id']=int(script_detail_id)
      script  =  ScriptDetails.objects.get(pk = (script_details['id']))
      serializer  =  ScriptsDetailSerializer(script, data = script_details)
      if serializer.is_valid():
        serializer.save()
        return Response({'status': True},status = 200)
      return Response({'status': False},status = 400)       
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

class RelativeOrderingAPI(generics.ListAPIView):
  def patch(self, request, script_id):
    script = Scripts.objects.get(pk=script_id)
    script.ordering = request.data['ordering']

    script.save()

    return Response({ 'status': True }, status=200)

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
      if script_data.comment_status == False:
        script_data.comment_status=True
        script_data.save()
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

class ReversionRevertView(generics.CreateAPIView):
  def patch(self,request,script_detail_id,reversion_id):
    try:
      script_detail=ScriptDetails.objects.get(pk=int(self.kwargs['script_detail_id']))
      reversion_data = Version.objects.get_for_object(script_detail)
      reversion_data[int(self.kwargs['reversion_id'])-1].revision.revert()
      return Response({'status': True},status = 201)
    except:
      return Response({'status': False},status = 400)
