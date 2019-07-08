# Create your tests here.
from django.test import TestCase

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class JwtTokenTest(APITestCase):
    jwt_token=" "

    def setUp(self):
        #create user
        user1 = User.objects.create_user("test1", "test@test.in", "Test@123")
        user2 = User.objects.create_user("test2", "test@test.in", "Test@123")
        user3 = User.objects.create_user("test3", "test@test.in", "Test@123")

        #create foss


    def test_check_jwt(self):
        url = reverse("jwt_token")
        data = {'username': 'test', 'password': 'Test@123'}
        response = self.client.post(url, data, format='json')
        self.jwt_token=(response.data['token'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 1)


