from rest_framework.routers import SimpleRouter

from users.views import UserViewSet


router = SimpleRouter()
router.register('', UserViewSet)

urlpatterns = router.urls
