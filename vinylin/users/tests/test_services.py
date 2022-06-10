from django.test import TestCase

from users.models import User
from users.services import UserService


class UserServiceTest(TestCase):
    @property
    def user_data(self):
        return {
            'email': 'test@mail.com',
            'password': 'DifficultPassword1',
            'first_name': 'First',
            'last_name': 'Last',
        }

    def setUp(self):
        User.objects.create_user(**self.user_data)

    def test_email_setter(self):
        email = self.user_data.get('email')
        user = User.objects.get(email=email)

        service = UserService()
        service.email = email

        self.assertEqual(user, service.user)

    def test_register(self):
        new_user_data = self.user_data
        new_user_data['email'] = 'foobar@mail.com'

        service = UserService()
        service.register(new_user_data)
        user = User.objects.filter(email=new_user_data.get('email'))

        self.assertTrue(user.exists())

    def test_change_email(self):
        email = self.user_data.get('email')
        new_email = 'foobar@mail.com'

        service = UserService()
        service.email = email
        service.change_email({'email': new_email})

        user = User.objects.filter(email=new_email)
        assert user.exists()

        self.assertEqual(user.first().email, new_email)

    def test_confirm_email(self):
        email = self.user_data.get('email')
        service = UserService()
        service.email = email
        service.confirm_email()

        self.assertTrue(User.objects.filter(email=email).exists())
