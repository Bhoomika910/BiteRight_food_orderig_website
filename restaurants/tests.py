from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from restaurants.models import MenuItem, Restaurant
from restaurants.nlp_service import detect_allergy_risk
from users.models import UserProfile


class AllergyDetectionTests(APITestCase):
    def test_allergy_detects_peanut(self):
        result = detect_allergy_risk(['peanut'], 'noodles with peanut oil')

        self.assertFalse(result['safe'])
        self.assertIn('peanut', result['matched_allergens'])

    def test_allergy_does_not_flag_coconut(self):
        result = detect_allergy_risk(['nut'], 'coconut milk curry')

        self.assertTrue(result['safe'])
        self.assertEqual(result['matched_allergens'], [])


class RecommendationAPITests(APITestCase):
    def setUp(self):
        self.auth_user = get_user_model().objects.create_user(
            username='food-user',
            email='food@example.com',
            password='password123',
        )
        self.token = Token.objects.create(user=self.auth_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.profile = UserProfile.objects.create(
            user=self.auth_user,
            name='Food User',
            email='food@example.com',
            allergies='peanut',
            diet_preferences='vegetarian',
        )
        self.restaurant = Restaurant.objects.create(
            name='Healthy Kitchen',
            rating=Decimal('4.50'),
        )
        self.safe_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Avocado Toast',
            price=Decimal('180.00'),
            diet_tags='Veg',
            mood_tags='healthy',
            ingredients='avocado, sourdough, seeds',
        )
        self.unsafe_item = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Peanut Noodles',
            price=Decimal('220.00'),
            diet_tags='Veg',
            mood_tags='healthy',
            ingredients='noodles, peanut sauce, vegetables',
        )
        self.url = reverse('recommendations', args=[self.restaurant.id])

    def test_recommendations_exclude_allergic_items(self):
        response = self.client.get(self.url, {'mood': 'healthy', 'time': 'late_night'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data['data']]
        self.assertIn(self.safe_item.name, names)
        self.assertNotIn(self.unsafe_item.name, names)

    def test_recommendations_include_reasons(self):
        response = self.client.get(self.url, {'mood': 'healthy', 'time': 'late_night'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['data'])
        self.assertIn('reasons', response.data['data'][0])
        self.assertTrue(response.data['data'][0]['reasons'])
