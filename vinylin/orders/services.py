from typing import Union

from django.core.exceptions import ValidationError
from django.db.models import QuerySet, F, Sum, DecimalField
from django.db import transaction

from orders.models import OrderItem, Order
from orders.emails import OrderEmailMessage
from store.models import Storage


class OrderItemService:
    def __init__(self, request):
        self._request = request
        self._cart = request.user.cart

        self.errors = {}

    @property
    def cart_items(self) -> QuerySet:
        return (
            OrderItem.objects.filter(cart=self._cart)
                             .order_by('product_id')
        )

    @property
    def order_items_(self) -> QuerySet:
        return (
            Order.objects.filter(user=self._request.user)
                         .prefetch_related('order_items')
        )

    def select_cart_item_modification(self, product_id, quantity):
        if quantity == 0:
            return self.delete_cart_item(product_id)
        return self.add_cart_item(product_id, quantity)

    def add_cart_item(self, product_id, quantity):
        if not self._is_quantity_valid(product_id, quantity):
            return None

        order_item, created_order_item = OrderItem.objects.get_or_create(
            cart=self._cart,
            order=None,
            product_id=product_id,
        )
        if not created_order_item:
            order_item.quantity = F('quantity') + quantity
            order_item.save()
        return order_item

    def change_cart_item_quantity(self, product_id, quantity):
        return (
            OrderItem.objects.filter(cart=self._cart, product_id=product_id)
                             .update(quantity=F('quantity') + quantity)
        )

    def delete_cart_item(self, product_id):
        return (
            OrderItem.objects.filter(cart=self._cart, product_id=product_id)
                             .delete()
        )

    @transaction.atomic
    def make_order(self):
        total_price = self._count_total_price(self.cart_items)
        discard_balance = self._discard_user_balance(
            self._request,
            total_price
        )
        if not discard_balance:
            self.errors = {'balance': ['You have not enough balance.']}
            return None

        self._update_storage(self.cart_items)

        new_order = Order.objects.create(
            user=self._request.user,
            status='PA',
            total_price=total_price,
        )
        self.cart_items.update(order=new_order, cart=None)

        order_items = OrderItem.objects.filter(order=new_order)
        self._mail_order(
            request=self._request,
            context=self._get_email_context(order_items, total_price)
        )
        return order_items

    def _is_quantity_valid(self, product_id, quantity):
        storage_quantity = Storage.objects.get(product_id=product_id).quantity
        if storage_quantity < quantity:
            self.errors.update({'quantity': ['Not enough products in stock.']})

            # self.errors.append('Not enough products in stock.')
            return False
        return True

    @staticmethod
    def _count_total_price(queryset):
        if not queryset.exists():
            return None
        return round(
            queryset.aggregate(Sum('final_price'))['final_price__sum'], 2)

    @staticmethod
    def _discard_user_balance(request, total_price):
        try:
            user_profile = request.user.profile
            new_user_balance = float(user_profile.balance) - float(total_price)

            decimal = DecimalField(max_digits=6, decimal_places=2)
            new_user_balance = str(round(new_user_balance, 2))
            new_user_balance = decimal.clean(new_user_balance,
                                             model_instance=None)
            user_profile.balance = new_user_balance
            user_profile.save()
            return user_profile

        except ValidationError:
            return None

    @staticmethod
    def _update_storage(queryset):
        """Updates the quantity of products in the storage"""
        storages = []
        for item in queryset.select_related('product__storage'):
            storage = item.product.storage
            storage.quantity = F('quantity') - item.quantity
            storages.append(storage)

        return Storage.objects.bulk_update(storages, ['quantity'])

    @staticmethod
    def _mail_order(request, context):
        message = OrderEmailMessage(request, context)
        return message.send(fail_silently=True)

    @staticmethod
    def _get_email_context(order_items, total_price):
        return {'order_items': order_items, 'total_price': total_price}