from django.core.exceptions import ValidationError
from django.db.models import QuerySet, F, Sum, DecimalField
from django.db import transaction, connection
from django.db.utils import IntegrityError

from orders.models import OrderItem, Order
from orders.emails import OrderEmailMessage


class OrderItemService:
    def __init__(self, request):
        self._request = request
        self._user = request.user
        self._cart = request.user.cart

        self.errors = {}

    @property
    def request(self):
        return self._request

    @property
    def user(self):
        return self._user

    @property
    def cart(self):
        return self._cart

    @property
    def cart_items(self) -> QuerySet:
        return (
            OrderItem.objects.filter(cart=self.cart)
                             .order_by('product_id')
        )

    @property
    def existing_order_items(self) -> QuerySet:
        return (
            Order.objects.filter(user=self.user)
                         .prefetch_related('order_items')
        )

    def select_cart_item_modification(self, product_id, quantity):
        if quantity == 0:
            return self.delete_cart_item(product_id)
        return self.add_or_update_cart_item(product_id, quantity)

    def add_or_update_cart_item(self, product_id, quantity):
        order_item, created_order_item = OrderItem.objects.get_or_create(
            cart=self.cart,
            order=None,
            product_id=product_id,
        )
        if not created_order_item:
            order_item.quantity = F('quantity') + quantity
            order_item.save()
        return order_item

    def change_cart_item_quantity(self, product_id, quantity):
        return (
            OrderItem.objects.filter(cart=self.cart, product_id=product_id)
                             .update(quantity=F('quantity') + quantity)
        )

    def delete_cart_item(self, product_id):
        return (
            OrderItem.objects.filter(cart=self.cart, product_id=product_id)
                             .delete()
        )

    @transaction.atomic
    def create_order(self):
        total_price = self._count_total_price(self.cart_items)
        discard_balance = self._discard_user_balance(
            self.user,
            total_price
        )
        if not discard_balance:
            return None

        storage_update = self._update_storage()
        if not storage_update:
            return None

        order = Order.objects.create(
            user=self.user,
            status='PA',
            total_price=total_price,
        )
        self.cart_items.update(order=order, cart=None)

        order_items = OrderItem.objects.filter(order=order)
        self._send_order_mail(
            request=self.request,
            context={'order_items': order_items, 'total_price': total_price}
        )
        return order_items

    @staticmethod
    def _count_total_price(queryset):
        if not queryset.exists():
            return None
        return round(
            queryset.aggregate(Sum('final_price'))['final_price__sum'], 2
        )

    def _discard_user_balance(self, user, total_price):
        try:
            user_profile = user.profile
            new_user_balance = float(user_profile.balance) - float(total_price)

            decimal = DecimalField(max_digits=6, decimal_places=2)
            new_user_balance = str(round(new_user_balance, 2))
            new_user_balance = decimal.clean(new_user_balance,
                                             model_instance=None)
            user_profile.balance = new_user_balance
            user_profile.save()
            return user_profile

        except ValidationError:
            self.errors.update({'balance': ['You have not enough balance.']})
            return None

    def _update_storage(self):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f'UPDATE store_storage ss SET quantity=(quantity - ('
                    f'SELECT oo.quantity FROM orders_orderitem oo '
                    f'WHERE oo.cart_id={self.cart.pk})) '
                    f'WHERE ss.product_id IN (SELECT oo.product_id '
                    f'FROM orders_orderitem oo '
                    f'WHERE oo.cart_id={self.cart.pk})'
                )
            return cursor.rowcount
        except IntegrityError:
            self.errors.update({'quantity': ['Not enough products in stock.']})
            return None

    @staticmethod
    def _send_order_mail(request, context):
        message = OrderEmailMessage(request, context)
        return message.send(fail_silently=True)
