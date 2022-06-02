from datetime import datetime

from django.contrib.auth import password_validation
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def birthday_validator(birthday):
    if birthday > datetime.today().date():
        raise ValidationError(
            _('Your birthday cannot be upper than today\'s date')
        )

    min_birthday = datetime.strptime('1872-01-01', '%Y-%m-%d').date()
    if birthday < min_birthday:
        raise ValidationError(
            _('Your birthday couldn\'t have been that long ago')
        )


def _validate_password(password, user):
    errors = {}
    try:
        password_validation.validate_password(
            password=password,
            user=user
        )
    except exceptions.ValidationError as e:
        errors['errors'] = list(e.messages)

    if errors:
        raise serializers.ValidationError(errors)
