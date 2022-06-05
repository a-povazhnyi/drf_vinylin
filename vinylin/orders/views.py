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
        return view_func(request)

    def show_cart(self, request):
        service = OrderItemService(request)
        serializer = CartSerializer(service.cart_items, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def change_cart_item(self, request):
        service = OrderItemService(request)
        serializer = CartItemSerializer(data=request.data)
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        service.select_cart_item_modification(
            product_id=serializer.data.get('product'),
            quantity=serializer.data.get('quantity')
        )

        if service.errors:
            return self.service_errors_response(service)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(url_path='make', methods=['PATCH'], detail=False)
    def make_order(self, request):
        service = OrderItemService(request)
        order = service.make_order()
        if service.errors:
            self.service_errors_response(service)

        serializer = OrderItemSerializer(order, many=True)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        return self.show_orders(request, *args, **kwargs)

    def show_orders(self, request, *args, **kwargs):
        service = OrderItemService(request)
        serializer = OrderSerializer(service.order_items_, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def non_valid_serializer_response(serializer):
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @staticmethod
    def service_errors_response(service):
        return Response(
            data={'errors': service.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
