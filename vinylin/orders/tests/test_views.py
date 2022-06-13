from unittest.mock import patch

from django.http import HttpRequest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from orders.services import OrderItemService
from store.models import Storage
from orders.models import OrderItem
from vinyl.models import Vinyl
from users.models import User


class OrderItemViewSetTest(APITestCase):
    @property
    def user_data(self):
        return {
            'email': 'test@mail.com',
            'password': 'DifficultPassword1',
            'first_name': 'First',
            'last_name': 'Last',
        }

    @property
    def vinyl_data(self):
        return {
            'title': 'Title',
            'price': '10.00',
            'part_number': '123ABC',
            'overview': '',
            'vinyl_title': 'Vinyl Title',
            'artist': None,
            'country': None,
            'format': 'format',
            'credits': 'Cool Credits'
        }

    @property
    def order_item_data(self):
        return {
            'cart': self.user.cart,
            'order': None,
            'product_id': self.vinyl.pk,
            'quantity': 10
        }

    def setUp(self):
        self.user = User.objects.create_user(**self.user_data)
        self.vinyl = Vinyl.objects.create(**self.vinyl_data)
        self.storage = Storage.objects.create(
            product_id=self.vinyl.pk,
            quantity=100
        )
        self.order_item = OrderItem.objects.create(**self.order_item_data)

        self.jwt_response = self.client.post(
            path=reverse('token_obtain_pair'),
            data={
                'email': self.user_data.get('email'),
                'password': self.user_data.get('password')
            },
            format='json'
        )
        self.access_token = self.jwt_response.data.get('access')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

        self.request = HttpRequest()
        self.request.user = self.user
        self.service = OrderItemService(self.request)

    def test_show_cart(self):
        response = self.client.get('/api/orders/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_cart_item(self):
        invalid_response = self.client.patch(
            path='/api/orders/cart/',
            data={'product': 100, 'quantity': 1},
            format='json'
        )
        self.assertEqual(invalid_response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        response = self.client.patch(
            path='/api/orders/cart/',
            data={'product': self.vinyl.pk, 'quantity': 1},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @staticmethod
    def mock_send_order_mail(request, context):
        return None

    @patch('orders.services.OrderItemService._send_order_mail',
           new=mock_send_order_mail)
    def test_create(self):
        invalid_response = self.client.post(path='/api/orders/')
        self.assertEqual(invalid_response.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.user.profile.balance = 1000
        self.user.profile.save()

        response = self.client.post(path='/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list(self):
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
