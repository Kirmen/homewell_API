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
    def setUp(self) -> None:
        category1 = Category.objects.create(name='Kitchen', slug='kitchen')
        category2 = Category.objects.create(name='Living room', slug='living-room')
        self.product1 = Product.objects.create(name='Super Table', slug='super-table', category=category1,
                                               description='The best table',
                                               price=200)
        self.product2 = Product.objects.create(name='Super Table2', slug='super-table2', category=category1,
                                               description='The second table',
                                               price=201, quantity=10)
        self.product3 = Product.objects.create(name='Super Sofa', slug='super-sofa', category=category2,
                                               description='The best sofa',
                                               price=202, quantity=15)

    def test_get(self):
        url = reverse('product-list')
        response = self.client.get(url)

        serializer_data = ProductSerializer([self.product1, self.product2, self.product3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_price_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'min_price': 200, 'max_price': 201})

        serializer_data = ProductSerializer([self.product1, self.product2], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_category_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'category': 'living-room'})

        serializer_data = ProductSerializer([self.product3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'search': 'super sofa'})

        serializer_data = ProductSerializer([self.product3], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_sort(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'ordering': '-price'})

        serializer_data = ProductSerializer([self.product3, self.product2, self.product1], many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)
