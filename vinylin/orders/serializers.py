from rest_framework import serializers

from orders.models import OrderItem
from vinyl.serializers import VinylSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'


class CartSerializer(OrderItemSerializer):
    product = VinylSerializer()

    class Meta:
        model = OrderItem
        exclude = ('order',)


class CartItemSerializer(OrderItemSerializer):
    quantity = serializers.IntegerField(required=True)

    def validate_quantity(self, value: int):
        if value > 0:
            ...
        return value

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


# class AddOrderItemSerializer(OrderItemSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ('product', 'quantity')
