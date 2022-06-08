from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated

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


class UserViewSet(RetrieveModelMixin, CreateModelMixin, GenericViewSet):
    model = User
    serializer_class = UserSerializer
    queryset = User.objects.all()

    @property
    def email_verification_map(self):
        return {
            'GET': self.send_email_confirmation,
            'PATCH': self.confirm_email
        }

    @property
    def password_reset_map(self):
        return {
            'POST': self.send_password_reset_email,
            'PATCH': self.confirm_password_reset
        }

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action == 'retrieve':
            return [IsOwner()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        service = UserService()
        serializer = RegistrationSerializer(
            data=request.data,
            context={'service': service}
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    @action(url_path='email', methods=['PATCH'], detail=False)
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

    @action(url_path='email/verification',
            methods=['GET', 'PATCH'],
            detail=False)
    def email_verification(self, request, *args, **kwargs):
        view_func = self.email_verification_map.get(request.method)
        return view_func(request, *args, **kwargs)

    def send_email_confirmation(self, request, *args, **kwargs):
        if request.user.is_email_verified:
            return self.not_verified_email_response

        UserService(user=request.user).send_confirm_message_email()
        return Response(status=status.HTTP_200_OK)

    def confirm_email(self, request, *args, **kwargs):
        if request.user.is_email_verified:
            return self.not_verified_email_response

        serializer = EmailConfirmSerializer(
            instance=request.user,
            data=request.data,
            context={'service': UserService(user=request.user)}
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(url_path='password', methods=['PATCH'], detail=False)
    def change_password(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(
            data=request.data,
            instance=request.user,
            context={'service': UserService(user=request.user)}
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        serializer.save()
        return Response(status=status.HTTP_202_ACCEPTED)

    @action(url_path='password/reset',
            methods=['POST', 'PATCH'],
            detail=False,
            permission_classes=[AllowAny])
    def reset_password(self, request, *args, **kwargs):
        view_func = self.password_reset_map.get(request.method)
        return view_func(request, *args, **kwargs)

    def send_password_reset_email(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(
            data=request.data,
            context={'service': UserService()}
        )
        if not serializer.is_valid():
            return self.non_valid_serializer_response(serializer)

        service = serializer.context.get('service')
        service.send_password_reset_email()
        return Response(status=status.HTTP_200_OK)

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

    @staticmethod
    def not_verified_email_response():
        return Response(
            data={'errors': ['User\'s e-mail is not verified.']},
            status=status.HTTP_400_BAD_REQUEST
        )
