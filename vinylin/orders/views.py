from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from orders.serializers import (
    OrderItemSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer
)
from orders.services import OrderItemService


class OrderItemViewSet(ViewSet):
    permission_classes = (IsAuthenticated,)

    @property
    def cart_map(self):
        return {
            'GET': self.show_cart,
            'PATCH': self.change_cart_item,
        }

    @action(url_path='cart', methods=['GET', 'PATCH'], detail=False)
    def cart(self, request, *args, **kwargs):
        view_func = self.cart_map.get(request.method)
        return view_func(request, *args, **kwargs)

    @staticmethod
    def show_cart(request, *args, **kwargs):
        service = OrderItemService(request)
        serializer = CartSerializer(service.cart_items, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def change_cart_item(self, request, *args, **kwargs):
        service = OrderItemService(request)
        serializer = CartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return self.non_valid_response(serializer=serializer)

        service.select_cart_item_modification(
            product_id=serializer.data.get('product'),
            quantity=serializer.data.get('quantity')
        )

        if service.errors:
            return self.non_valid_response(service=service)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """Show all user`s orders"""
        service = OrderItemService(request)
        serializer = OrderSerializer(service.existing_order_items, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Create and return order or errors if exist"""
        service = OrderItemService(request)
        order = service.create_order()
        if service.errors:
            return self.non_valid_response(service=service)

        serializer = OrderItemSerializer(order, many=True)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def non_valid_response(serializer=None, service=None):
        if serializer or service:
            return Response(
                data=serializer.errors if serializer else service.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_400_BAD_REQUEST)
