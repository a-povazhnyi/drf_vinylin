from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            f'{text_type(user.pk)}{text_type(timestamp)}'
            f'{text_type(user.is_email_verified)}'
        )
