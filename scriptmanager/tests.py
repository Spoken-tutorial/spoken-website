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


class TestScriptmanagerAPI(APITestCase):
    client = APIClient()
    var={}


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

        tutorial1=TutorialDetail.objects.create(foss=self.foss1,tutorial="test data 1",level=level,order=1,user=test1)
        tutorial2=TutorialDetail.objects.create(foss=self.foss1,tutorial="test data 2",level=level,order=2,user=test1)
        
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

    def test_scripts_module(self):
        self.client.login(username='test1', password='Test@123')

        #get the foss
        foss_url="/scripts/api/foss/"
        response =self.client.get(foss_url)
        fid=response.data[0]['foss_category']['id']
        lid=response.data[0]['language']['id']
        self.assertEqual(fid,self.foss1.pk)
        self.assertEqual(lid,self.lang1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        #get the tutorials for a foss category
        tutorial_url="/scripts/api/foss/"+str(fid)+"/language/"+str(lid)+"/tutorials/"
        response =self.client.get(tutorial_url)
        fid=response.data[0]['foss']
        lid=response.data[0]['language']
        self.assertEqual(fid,self.foss1.pk)
        self.assertEqual(lid,self.lang1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



