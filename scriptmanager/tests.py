# Create your tests here.
from django.test import TestCase

from django.test import Client
from rest_framework.test import APIClient
from creation.models import ContributorRole, FossCategory, Language, TutorialDetail,TutorialResource,FossSuperCategory,Level
from scriptmanager.models import Scripts, ScriptDetails, Comments
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import time


class TestScriptmanagerAPI(APITestCase):
    client = APIClient()

    def setUp(self):
        test1=User.objects.create_user("test1", "test2@test2.in", "Test@123")
        test2=User.objects.create_user("test2", "test2@test2.in", "Test@123")
        test3=User.objects.create_user("test3", "test2@test2.in", "Test@123")
        test4=User.objects.create_user("test4", "test2@test2.in", "Test@123")

        self.lang1=Language.objects.create(name="test_Tamil",user=test1)
        lang2=Language.objects.create(name="test_English",user=test2)
        lang3=Language.objects.create(name="test_Kannada",user=test3)

        self.foss1=FossCategory.objects.create(foss="test_Blender",description="testing data",status=True,user=test1)
        foss2=FossCategory.objects.create(foss="test_Python",description="testing data",status=True,user=test1)
        foss3=FossCategory.objects.create(foss="test_Advanced C++",description="testing data",status=True,user=test1)

        cont1 = ContributorRole.objects.create(foss_category=self.foss1,language=self.lang1,user=test1,status=True)
        cont2 = ContributorRole.objects.create(foss_category=foss2,language=lang2,user=test2,status=True)
        cont3 = ContributorRole.objects.create(foss_category=foss3,language=lang3,user=test3,status=True)

        level=Level.objects.create(level="test level",code="TL")

        self.tutorial1=TutorialDetail.objects.create(foss=self.foss1,tutorial="test data 1",level=level,order=1,user=test1)
        tutorial2=TutorialDetail.objects.create(foss=self.foss1,tutorial="test data 2",level=level,order=2,user=test1)
        
        self.client.login(username='test1', password='Test@123')

        self.scripts_url="/scripts/api/tutorial/"+str(self.tutorial1.pk)+"/language/"+str(self.lang1.pk)+"/scripts/"
        self.script_data={"type":"form","details":[{"cue":"test","narration":"test","order":1},{"cue":"test2","narration":"test2","order": 2}]}

        #test objects are created
        self.assertEqual(User.objects.count(), 4)
        self.assertEqual(Language.objects.count(), 3)
        self.assertEqual(FossCategory.objects.count(), 3)
        self.assertEqual(ContributorRole.objects.count(),3)
        self.assertEqual(TutorialDetail.objects.count(),2)

    def test_get_jwt(self):
        #check jwt token is retured or not
        url = reverse("jwt_token")
        data = {'username': 'test1', 'password': 'Test@123'}        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_foss(self):
        foss_url="/scripts/api/foss/"
        response =self.client.get(foss_url)
        self.assertEqual(response.data[0]['foss_category']['id'],self.foss1.pk)
        self.assertEqual(response.data[0]['language']['id'],self.lang1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_tutorials(self):        
        tutorial_url="/scripts/api/foss/"+str(self.foss1.pk)+"/language/"+str(self.lang1.pk)+"/tutorials/"
        response =self.client.get(tutorial_url)
        self.assertEqual(response.data[0]['foss'],self.foss1.pk)
        self.assertEqual(response.data[0]['language'],self.lang1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_scripts(self):
        response=self.client.post(self.scripts_url,self.script_data,format='json')
        self.assertEqual(response.data['status'],True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

     
    def test_get_scripts(self):
        self.client.post(self.scripts_url,self.script_data,format='json')
        response=self.client.get(self.scripts_url)
        self.assertEqual(len(response.data),2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_patch_scripts(self):
        self.client.post(self.scripts_url,self.script_data,format='json')
        response=self.client.get(self.scripts_url)
        pk=response.data[0]['id']
        data={"cue":"patch req","narration":"from test.py","order":1}
        response=self.client.patch(self.scripts_url+str(pk)+"/",data,format='json')
        self.assertEqual(response.data['status'],True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_scripts(self):
        self.client.post(self.scripts_url,self.script_data,format='json')
        response=self.client.get(self.scripts_url)
        self.assertEqual(len(response.data),2)
        response=self.client.delete(self.scripts_url+str(response.data[0]['id'])+"/")
        response=self.client.get(self.scripts_url)
        self.assertEqual(len(response.data),1)


