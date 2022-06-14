from django.core.mail import EmailMessage
from django.conf import settings


class EmailConfirmMessage(EmailMessage):
    def __init__(self, code, *args, **kwargs):
        """to keyword argument should be specified during initialization"""
        super().__init__(*args, **kwargs)

        self.code = code
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.subject = 'Confirm your e-mail'
        self.body = f'Here is your e-mail verification code: \n{self.code}'
