from rest_framework import status
from rest_framework.test import APITestCase

from vinyl.models import Vinyl


class VinylViewSetTest(APITestCase):
    def setUp(self):
        self.vinyl = Vinyl.objects.create(**self.vinyl_data)

        new_vinyl_data = self.vinyl_data
        new_vinyl_data['part_number'] = '456DEF'
        Vinyl.objects.create(**new_vinyl_data)

    @property
    def vinyl_data(self):
        return {
            'title': 'Title',
            'price': '10.00',
            'part_number': '123ABC',
            'overview': '',
            'vinyl_title': 'Vinyl Title',
            'artist': None,
            'country': None,
            'format': 'format',
            'credits': 'Cool Credits'
        }

    def test_retrieve(self):
        response = self.client.get(f'/api/vinyl/{self.vinyl.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('id'), self.vinyl.pk)

    def test_list(self):
        response = self.client.get('/api/vinyl/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
