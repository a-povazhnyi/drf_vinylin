from rest_framework import serializers

from orders.models import OrderItem, Order
from vinyl.serializers import VinylSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = VinylSerializer()

    class Meta:
        model = OrderItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    product = VinylSerializer()

    class Meta:
        model = OrderItem
        exclude = ('order',)


class CartItemSerializer(serializers.ModelSerializer):
    quantity = serializers.IntegerField(required=True)

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'status', 'total_price', 'order_items')
