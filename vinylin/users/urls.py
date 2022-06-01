from django.urls import path
from rest_framework.routers import SimpleRouter

from users.views import (
    UserViewSet,
    EmailVerificationView,
    EmailConfirmView,
    EmailChangeView,
    PasswordChangeView,
)


router = SimpleRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('email/verification/', EmailVerificationView.as_view()),
    path('email/confirm/', EmailConfirmView.as_view()),
    path('email/change/', EmailChangeView.as_view()),

    path('password/change/', PasswordChangeView.as_view()),
]
urlpatterns += router.urls
