from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APITestCase

from orders.services import OrderItemService
from orders.tests.fixtures import orders_fixture


@pytest.mark.usefixtures('orders_fixture')
class OrderItemViewSetTest(APITestCase):
    def setUp(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )
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
