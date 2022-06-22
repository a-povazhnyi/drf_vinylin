from datetime import timedelta

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from rest_framework import serializers

from users.emails import EmailConfirmMessage
from users.models import User, Profile
from users.tasks import (
    send_confirm_email_task,
    send_password_reset_email_task,
    send_site_reminder_task
)
from users.tokens import TokenGenerator


class UserService:
    def __init__(self, user=None):
        self._user_model = User
        self._profile_model = Profile

        self._user: User = user
        self._email = None

        self._token_generator = TokenGenerator()

    @property
    def user_model(self):
        return self._user_model

    @property
    def profile_model(self):
        return self._profile_model

    @property
    def user(self):
        return self._user

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        queryset = User.objects.filter(email=value)
        if not queryset.exists():
            self._user = None
            self._email = None
        else:
            user = queryset.first()
            self._user = user
            self._email = user.email

    @property
    def token_generator(self):
        return self._token_generator

    def validate_password(self, password):
        errors = {}
        try:
            password_validation.validate_password(
                password=password,
                user=self.user
            )
        except ValidationError as e:
            errors['errors'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

    def register(self, data):
        profile = data.pop('profile', None)
        user = self.user_model.objects.create_user(**data)

        if profile:
            self.profile_model.objects.filter(user=user).update(**profile)
        return user

    def change_email(self, data):
        self.user.is_email_verified = False
        self.user.email = data.get('email')
        self.user.save()
        return self.user

    def confirm_email(self):
        self.user.is_email_verified = True
        self.user.save()
        return self.user

    def send_confirm_message_email(self):
        token = self._make_token()
        send_confirm_email_task.delay(token=token, email=self.user.email)

    def send_password_reset_email(self):
        token = self._make_token()
        send_password_reset_email_task.delay(token=token,
                                             email=self.user.email)

    def send_site_reminder(self):
        send_site_reminder_task.apply_async(
            [self.user.email],
            countdown=int(timedelta(days=3).total_seconds()),
            expires=int(timedelta(days=14).total_seconds())
        )

    def set_password(self, password):
        self.user.set_password(password)
        self.user.save()

    def is_token_valid(self, token):
        return self.token_generator.check_token(user=self.user, token=token)

    def _make_token(self):
        return self.token_generator.make_token(self.user)

    def _get_password_reset_email(self, token):
        password_reset_email = EmailConfirmMessage(
            code=token,
            to=[self.user.email]
        )
        password_reset_email.subject = 'Reset your password!'
        password_reset_email.body = (
            f'Here is your password reset code: \n{token}'
        )
        return password_reset_email

    def _get_confirm_email_message(self, token):
        return EmailConfirmMessage(
            code=token,
            to=[self.user.email]
        )
