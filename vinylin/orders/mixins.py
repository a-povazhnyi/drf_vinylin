from django.contrib.auth.mixins import UserPassesTestMixin


class UserOrdersPermissionMixin(UserPassesTestMixin):
    request = None
    kwargs = None

    def test_func(self):
        assert self.request is not None
        assert self.kwargs is not None
        return self.request.user.cart.pk == self.kwargs.get('cart_pk')
