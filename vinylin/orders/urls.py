from rest_framework.routers import DefaultRouter

from orders.views import OrderItemViewSet

router = DefaultRouter()
router.register('', OrderItemViewSet, basename='orders')

urlpatterns = router.urls
