import pytest
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import AccessToken

from orders.models import OrderItem
from store.models import Storage
from users.models import User
from vinyl.models import Vinyl


@pytest.fixture(scope='class')
def orders_fixture(request):
    user_data = {
        'email': 'test@mail.com',
        'password': 'DifficultPassword1',
        'first_name': 'First',
        'last_name': 'Last',
    }
    vinyl_data = {
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
    user = User.objects.create_user(**user_data)
    vinyl = Vinyl.objects.create(**vinyl_data)
    storage = Storage.objects.create(
        product_id=vinyl.pk,
        quantity=100
    )

    order_item_data = {
        'cart': user.cart,
        'order': None,
        'product_id': vinyl.pk,
        'quantity': 10
    }
    order_item = OrderItem.objects.create(**order_item_data)

    http_request = HttpRequest()
    http_request.user = user

    access_token = AccessToken.for_user(user)

    request.cls.user_data = user_data
    request.cls.user = user
    request.cls.vinyl_data = vinyl_data
    request.cls.vinyl = vinyl
    request.cls.storage = storage
    request.cls.order_item_data = order_item_data
    request.cls.order_item = order_item
    request.cls.request = http_request
    request.cls.access_token = access_token
