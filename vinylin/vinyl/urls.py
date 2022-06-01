from rest_framework.routers import SimpleRouter

from vinyl.views import VinylViewSet


router = SimpleRouter()
router.register(r'', VinylViewSet)

urlpatterns = router.urls
