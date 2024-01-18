import os

import django
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Product, Category
from store.serializers import ProductSerializer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homewell.settings')
if not settings.configured:
    django.setup()


class HomewellApiTestCase(APITestCase):
    def test_get(self):
        category1 = Category.objects.create(name='Kitchen')
        product1 = Product.objects.create(name='SuperTable', category=category1, description='The best table',
                                          price=200)
        product2 = Product.objects.create(name='SuperTable2', category=category1, description='The second table',
                                          price=201)

        url = reverse('product-list')
        response = self.client.get(url)

        serializer_data = ProductSerializer([product1, product2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
