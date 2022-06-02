from users.emails import EmailConfirmMessage
from users.models import User
from users.tokens import TokenGenerator


class UserService:
    def __init__(self, request=None):
        self.request = request
        self._user: User = request.user if request else None
        self._token_generator = TokenGenerator()

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, email):
        queryset = User.objects.filter(email=email)
        if not queryset.exists():
            self._user = None
        else:
            self._user = queryset.first()

    @property
    def token_generator(self):
        return self._token_generator

    def send_confirm_message_email(self):
        token = self._make_token()
        email_confirm = self._get_confirm_email_message(token)
        return email_confirm.send(fail_silently=True)

    def send_password_reset_email(self):
        token = self._make_token()
        password_reset_email = self._get_password_reset_email(token)
        return password_reset_email.send(fail_silently=True)

    def set_new_password(self, password):
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
