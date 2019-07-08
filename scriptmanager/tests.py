# Create your tests here.
from django.test import TestCase


from creation.models import ContributorRole, FossCategory, Language, TutorialDetail,TutorialResource,FossSuperCategory
from scriptmanager.models import Scripts, ScriptDetails, Comments
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestScriptmanagerAPI(APITestCase):
    jwt_token=" "
    users=[]
    lang_obj=[]
    foss_obj=[]
    

    def setUp(self):
        #create user
        user=["admin","test1","test2"]
        for x in user:
            self.users.append(User.objects.create_user(x, "test@test.in", "Test@123"))

        #create languge
        lang=["Tamil","English","Kannada","Telugu","Hindi"]
        lang_code=["ta","en","kn","te","hi"]
        for x in range(len(lang)):
            self.lang_obj.append(Language.objects.create(name=lang[x],user=self.users[0],code=lang_code[x]))

        #create foss
        foss_data=["Blender","Firefox","GIMP","Drupal","Java"]
        for x in foss_data:
            self.foss_obj.append(FossCategory.objects.create(foss=x,status=True,user=self.users[0]))

        #create contributor role
        for x in self.foss_obj:
            for y in self.lang_obj:
                ContributorRole.objects.create(foss_category=x,language=y,user=self.users[0],status=True)

        #test objects are created
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(Language.objects.count(), 5)
        self.assertEqual(FossCategory.objects.count(), 5)
        self.assertEqual(ContributorRole.objects.count(), 25)

    def test_get_jwt(self):
        url = reverse("jwt_token")
        data = {'username': 'test1', 'password': 'Test@123'}
        response = self.client.post(url, data, format='json')
        self.jwt_token=(response.data['token'])
        print(self.jwt_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



    
  

    

