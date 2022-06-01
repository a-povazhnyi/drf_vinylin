from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from users.emails import EmailConfirmMessage
from users.models import User
from users.permissions import IsOwner
from users.tokens import TokenGenerator
from users.serializers import (
    UserSerializer,
    RegistrationSerializer,
    EmailChangeSerializer,
    EmailConfirmSerializer,
    PasswordChangeSerializer,
    PasswordResetConfirmSerializer
)


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @action(url_path='register', methods=['post'], detail=False)
    def register(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def get_authenticators(self):
        if self.action_map.get('post') == 'register':
            return None
        return super().get_authenticators()

    def get_permissions(self):
        if self.action == 'register':
            return [AllowAny()]
        return [IsOwner()]


class EmailVerificationView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.is_email_verified:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        token = TokenGenerator().make_token(user)
        email_confirm = EmailConfirmMessage(
            code=token,
            to=[user.email]
        )
        email_confirm.send(fail_silently=True)
        return Response(status=status.HTTP_200_OK)


class EmailConfirmView(UpdateAPIView):
    http_method_names = ('put',)

    def put(self, request, *args, **kwargs):
        serializer = EmailConfirmSerializer(
            instance=request.user,
            data=request.data
        )
        if not serializer.is_valid():
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class EmailChangeView(UpdateAPIView):
    http_method_names = ('put',)

    def put(self, request, *args, **kwargs):
        serializer = EmailChangeSerializer(
            data=request.data,
            instance=request.user,
        )

        if not serializer.is_valid():
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_202_ACCEPTED
        )


class PasswordChangeView(UpdateAPIView):
    http_method_names = ('put',)

    def put(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(
            data=request.data,
            instance=request.user,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)


class PasswordResetView(CreateAPIView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if not user.is_email_verified:
            return Response(
                data={'password_reset': {
                    'errors': ['Email is not verified.']
                }},
                status=status.HTTP_400_BAD_REQUEST
            )

        self._send_password_reset_email(user)
        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def _send_password_reset_email(user):
        token = TokenGenerator().make_token(user)
        password_reset_email = EmailConfirmMessage(
            code=token,
            to=[user.email]
        )
        password_reset_email.subject = 'Reset your password'
        password_reset_email.body = (
            f'Here is your password reset code: \n{token}'
        )
        return password_reset_email.send(fail_silently=True)


class PasswordResetConfirmView(UpdateAPIView):
    http_method_names = ('put',)

    def put(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(
            data=request.data,
            instance=request.user
        )
        if not serializer.is_valid():
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)
