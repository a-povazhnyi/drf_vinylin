from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from users.models import User
from users.services import UserService


class UserViewSetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**self.user_data)
        self.anonymous_client = APIClient()
        self.service = UserService(user=self.user)

        self.jwt_response = self.client.post(
            path=reverse('token_obtain_pair'),
            data={
                'email': self.user_data.get('email'),
                'password': self.user_data.get('password')
            },
            format='json'
        )
        self.access_token = self.jwt_response.data.get('access')

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}'
        )

    @property
    def user_data(self):
        return {
            'email': 'test@mail.com',
            'password': 'DifficultPassword1',
            'first_name': 'First',
            'last_name': 'Last',
        }

    def test_create(self):
        data = {
            'email': 'testcreation@mail.com',
            'password': 'DifficultPassword1',
            'first_name': 'First',
            'last_name': 'Last',
        }
        response = self.anonymous_client.post(
            '/api/users/',
            data=data,
            format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_retrieve(self):
        response = self.client.get(f'/api/users/{self.user.pk}/')
        invalid_response = self.client.get(f'/api/users/{self.user.pk + 1}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            invalid_response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_change_email(self):
        response = self.client.patch(
            '/api/users/email/',
            data={'email': 'foobar@mail.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_email_verification(self):
        response1 = self.client.get('/api/users/email/verification/')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)

        token = self.service._make_token()
        response2 = self.client.patch(
            '/api/users/email/verification/',
            data={'token': token},
            format='json'
        )
        self.assertEqual(response2.status_code, status.HTTP_202_ACCEPTED)

    def test_reset_password(self):
        invalid_response1 = self.anonymous_client.post(
            '/api/users/password/reset/',
            data={'email': self.user_data.get('email')},
            format='json'
        )
        self.assertEqual(invalid_response1.status_code,
                         status.HTTP_400_BAD_REQUEST)

        self.service.confirm_email()
        valid_response1 = self.anonymous_client.post(
            path='/api/users/password/reset/',
            data={'email': self.user_data.get('email')},
            format='json'
        )
        self.assertEqual(valid_response1.status_code, status.HTTP_200_OK)

        token = self.service._make_token()
        response = self.anonymous_client.patch(
            path='/api/users/password/reset/',
            data={
                'email': self.user_data.get('email'),
                'token': token,
                'new_password': 'NewDifficultPassword1'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
