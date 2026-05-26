from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from restaurants.models import MenuItem, Restaurant
from users.models import UserProfile


class OrderAPITests(APITestCase):
    def setUp(self):
        self.auth_user = get_user_model().objects.create_user(
            username='order-user',
            email='order@example.com',
            password='password123',
        )
        self.token = Token.objects.create(user=self.auth_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.profile = UserProfile.objects.create(
            user=self.auth_user,
            name='Order User',
            email='order@example.com',
            allergies='',
            diet_preferences='vegetarian',
        )
        self.restaurant = Restaurant.objects.create(name='Green Bowl')
        self.other_restaurant = Restaurant.objects.create(name='Spice House')

        self.salad = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Quinoa Salad',
            price=Decimal('120.00'),
            diet_tags='Veg',
            mood_tags='healthy',
            ingredients='quinoa, greens, lemon',
        )
        self.toast = MenuItem.objects.create(
            restaurant=self.restaurant,
            name='Avocado Toast',
            price=Decimal('80.00'),
            diet_tags='Veg',
            mood_tags='healthy',
            ingredients='avocado, sourdough',
        )
        self.other_item = MenuItem.objects.create(
            restaurant=self.other_restaurant,
            name='Paneer Tikka',
            price=Decimal('150.00'),
            diet_tags='Veg',
            mood_tags='spicy',
            ingredients='paneer, spices',
        )
        self.url = reverse('order-list-create')

    def test_create_order_success(self):
        payload = {
            'restaurant': self.restaurant.id,
            'items': [
                {'menu_item': self.salad.id, 'quantity': 2},
                {'menu_item': self.toast.id, 'quantity': 1},
            ],
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(response.data['data']['subtotal']), Decimal('320.00'))
        # Backend now includes 5% tax so saved total matches cart total.
        self.assertEqual(Decimal(response.data['data']['tax']), Decimal('16.00'))
        self.assertEqual(Decimal(response.data['data']['total_price']), Decimal('336.00'))

    def test_create_order_invalid_item(self):
        payload = {
            'restaurant': self.restaurant.id,
            'items': [{'menu_item': 999999, 'quantity': 1}],
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data['errors'])

    def test_mixed_restaurant_error(self):
        payload = {
            'restaurant': self.restaurant.id,
            'items': [
                {'menu_item': self.salad.id, 'quantity': 1},
                {'menu_item': self.other_item.id, 'quantity': 1},
            ],
        }

        response = self.client.post(self.url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('items', response.data['errors'])

    def test_orders_requires_authentication(self):
        self.client.credentials()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
