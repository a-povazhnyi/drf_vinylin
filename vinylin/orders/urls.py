from rest_framework.routers import DefaultRouter

from orders.views import OrderItemViewSet

router = DefaultRouter()
router.register('', OrderItemViewSet)

urlpatterns = router.urls
