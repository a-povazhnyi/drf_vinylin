from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from users.models import User
from users.permissions import IsOwner
from users.serializers import (
    UserSerializer,
    RegistrationSerializer,
    EmailChangeSerializer,
    EmailConfirmSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)
from users.services import UserService


class UserViewSet(ModelViewSet):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsOwner]

    @action(url_path='register',
            methods=['post'],
            detail=False,
            permission_classes=[AllowAny])
    def register(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(url_path='email/verification', methods=['get'], detail=False)
    def email_verification(self, request, *args, **kwargs):
        if request.user.is_email_verified:
            return self.not_verified_email_response

        UserService(request=request).send_confirm_message_email()
        return Response(status=status.HTTP_200_OK)

    @action(url_path='email/confirm', methods=['put'], detail=False)
    def confirm_email(self, request, *args, **kwargs):
        if request.user.is_email_verified:
            return self.not_verified_email_response

        serializer = EmailConfirmSerializer(
            instance=request.user,
            data=request.data,
            context={'service': UserService()}
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(url_path='email/change', methods=['put'], detail=False)
    def change_email(self, request, *args, **kwargs):
        serializer = EmailChangeSerializer(
            data=request.data,
            instance=request.user,
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_202_ACCEPTED
        )

    @action(url_path='password/change', methods=['put'], detail=False)
    def change_password(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(
            data=request.data,
            instance=request.user,
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(url_path='password/reset',
            methods=['post'],
            detail=False,
            permission_classes=[AllowAny])
    def reset_password(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(
            data=request.data,
            context={'service': UserService()}
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        service = UserService()
        service.user = serializer.data.get('email')
        service.send_password_reset_email()
        return Response(status=status.HTTP_200_OK)

    @action(url_path='password/reset/confirm',
            methods=['put'],
            detail=False,
            permission_classes=[AllowAny])
    def confirm_password_reset(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(
            data=request.data,
            context={'service': UserService()}
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    @staticmethod
    def non_valid_serializer_response(serializer):
        return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    @property
    def not_verified_email_response(self):
        return Response(
            data={'errors': ['User\'s e-mail is not verified.']},
            status=status.HTTP_400_BAD_REQUEST
        )
