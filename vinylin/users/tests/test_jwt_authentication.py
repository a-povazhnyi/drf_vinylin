from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User


class JWTAuthorizationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(**self.user_data)

        self.jwt_response = self.client.post(
            path=reverse('token_obtain_pair'),
            data={'email': 'test@mail.com', 'password': 'DifficultPassword1'},
            format='json'
        )

    @property
    def user_data(self):
        return {
            'email': 'test@mail.com',
            'password': 'DifficultPassword1',
            'first_name': 'First',
            'last_name': 'Last',
        }

    def test_jwt(self):
        self.assertEqual(self.jwt_response.status_code, status.HTTP_200_OK)
        self.assertTrue('refresh' in self.jwt_response.data)
        self.assertTrue('access' in self.jwt_response.data)

    def test_refresh_token(self):
        refresh_token = self.jwt_response.data.get('refresh')
        response = self.client.post(
            path=reverse('token_refresh'),
            data={'refresh': refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)

    def test_authorized_request(self):
        access_token = self.jwt_response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.get(f'/api/users/{self.user.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
