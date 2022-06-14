from unittest.mock import patch

import pytest
from django.test import TestCase

from orders.models import OrderItem, Order
from orders.services import OrderItemService
from orders.tests.fixtures import orders_fixture
from store.models import Storage
from users.models import Profile
from vinyl.models import Vinyl


@pytest.mark.usefixtures('orders_fixture')
class OrderItemServiceTest(TestCase):
    def setUp(self):
        self.user.profile.balance = 1000
        self.user.profile.save()

        self.service = OrderItemService(self.request)

    def test_add_cart_item(self):
        new_vinyl_data = self.vinyl_data
        new_vinyl_data['part_number'] = '456DEF'
        new_vinyl = Vinyl.objects.create(**new_vinyl_data)

        new_order_item_data = self.order_item_data
        new_order_item_data['product_id'] = new_vinyl.pk

        order_item = self.service.add_or_update_cart_item(
            product_id=new_order_item_data.get('product_id'),
            quantity=1,
        )
        self.assertTrue(OrderItem.objects.filter(pk=order_item.pk).exists())

    def test_update_cart_item(self):
        increase_quantity_by = 3
        decrease_quantity_by = 2

        self.service.add_or_update_cart_item(
            product_id=self.vinyl.pk,
            quantity=increase_quantity_by
        )
        updated_order_item1 = OrderItem.objects.get(pk=self.order_item.pk)
        self.assertEqual(self.order_item.pk, updated_order_item1.pk)
        self.assertEqual(
            self.order_item.quantity + increase_quantity_by,
            updated_order_item1.quantity
        )

        self.service.add_or_update_cart_item(
            product_id=self.vinyl.pk,
            quantity=-decrease_quantity_by
        )
        updated_order_item2 = OrderItem.objects.get(pk=self.order_item.pk)
        self.assertEqual(
            updated_order_item1.quantity - decrease_quantity_by,
            updated_order_item2.quantity
        )

    def test_count_total_price(self):
        total_price = self.service._count_total_price(self.service.cart_items)
        self.assertEqual(
            total_price,
            self.order_item.quantity * self.order_item.product.price
        )

    def test_discard_user_balance(self):
        last_balance = self.user.profile.balance
        total_price = self.service._count_total_price(self.service.cart_items)
        self.service._discard_user_balance(
            user=self.user,
            total_price=total_price
        )

        current_balance = Profile.objects.get(user=self.user).balance
        self.assertEqual(current_balance, last_balance - total_price)

        overprice = 1001.00
        discard_balance = self.service._discard_user_balance(
            user=self.user,
            total_price=overprice
        )
        self.assertIs(discard_balance, None)

    def test_update_storage(self):
        self.service._update_storage()
        current_storage_quantity = (
            Storage.objects.get(product_id=self.vinyl.pk).quantity
        )
        self.assertEqual(
            current_storage_quantity,
            self.storage.quantity - self.order_item.quantity
        )

        self.storage.quantity = 0
        self.storage.save()
        storage_update = self.service._update_storage()
        self.assertIs(storage_update, None)

    @staticmethod
    def mock_send_order_mail(request, context):
        return None

    @patch('orders.services.OrderItemService._send_order_mail',
           new=mock_send_order_mail)
    def test_create_order(self):
        self.service.create_order()
        self.assertTrue(Order.objects.filter(user=self.user).exists())
