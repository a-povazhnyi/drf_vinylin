from django.contrib.auth import password_validation
from django.core import exceptions
from rest_framework import serializers


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
