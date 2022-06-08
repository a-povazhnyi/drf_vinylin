from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


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
