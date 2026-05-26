from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users.models import UserProfile


class UserProfileAPITests(APITestCase):
    def setUp(self):
        self.auth_user = get_user_model().objects.create_user(
            username='profile-user',
            email='profile@example.com',
            password='password123',
        )
        self.token = Token.objects.create(user=self.auth_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.profile = UserProfile.objects.create(
            user=self.auth_user,
            name='Profile User',
            email='profile@example.com',
            allergies='peanut',
            diet_preferences='vegetarian',
        )

    def test_get_user_detail_success(self):
        url = reverse('user-detail', args=[self.profile.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['id'], self.profile.id)
        self.assertEqual(response.data['data']['email'], self.profile.email)
