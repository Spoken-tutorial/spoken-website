# Create your tests here.
from django.test import TestCase

from django.test import Client
from rest_framework.test import APIClient
from creation.models import ContributorRole, FossCategory, Language, TutorialDetail,TutorialResource,FossSuperCategory
from scriptmanager.models import Scripts, ScriptDetails, Comments
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestScriptmanagerAPI(APITestCase):
    client = APIClient()
    

    def setUp(self):
        #create user
        # user=["admin","test1","test2"]
        # for x in user:
        #     self.users.append(User.objects.create_user(x, "test@test.in", "Test@123"))


        test1=User.objects.create_user("test1", "test2@test2.in", "Test@123")
        test2=User.objects.create_user("test2", "test2@test2.in", "Test@123")
        test3=User.objects.create_user("test3", "test2@test2.in", "Test@123")


        lang1=Language.objects.create(name="test_Tamil",user=test1)
        lang2=Language.objects.create(name="test_English",user=test2)
        lang3=Language.objects.create(name="test_Kannada",user=test3)


        self.foss1=FossCategory.objects.create(foss="test_Blender",description="testing data",status=True,user=test1)
        foss2=FossCategory.objects.create(foss="test_Python",description="testing data",status=True,user=test1)
        foss3=FossCategory.objects.create(foss="test_Advanced C++",description="testing data",status=True,user=test1)

        cont1 = ContributorRole.objects.create(foss_category=self.foss1,language=lang1,user=test1,status=True)
        cont2 = ContributorRole.objects.create(foss_category=foss2,language=lang2,user=test2,status=True)
        cont3 = ContributorRole.objects.create(foss_category=foss3,language=lang3,user=test3,status=True)

        #test objects are created
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Language.objects.count(), 3)
        self.assertEqual(FossCategory.objects.count(), 3)
        self.assertEqual(ContributorRole.objects.count(),3)

    def test_get_jwt(self):
        url = reverse("jwt_token")
        data = {'username': 'test1', 'password': 'Test@123'}        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_get_foss(self):
        self.client.login(username='test1', password='Test@123')
        response =self.client.get("/scripts/api/foss/")
        self.assertEqual(response.data[0]['foss_category']['id'],self.foss1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.logout()


        



    
  

    

