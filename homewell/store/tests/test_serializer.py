from collections import OrderedDict

from django.test import TestCase

from store.models import Category, Product
from store.serializers import ProductSerializer


class ProductSerializerTestCase(TestCase):
    def test_ok(self):
        category1 = Category.objects.create(name='Kitchen')
        product1 = Product.objects.create(name='SuperTable', category=category1, description='The best table',
                                          price=200)
        product2 = Product.objects.create(name='SuperTable2', category=category1, description='The second table',
                                          price=201)
        data = ProductSerializer([product1, product2], many=True).data

        expected_data = [
            {
                'id': product1.id,
                'category': OrderedDict([('name', 'Kitchen')]),
                'images': [],
                'name': 'SuperTable',
                'description' : 'The best table',
                'price' : '200.00'

            },
            {
                'id': product2.id,
                'category': OrderedDict([('name', 'Kitchen')]),
                'images': [],
                'name': 'SuperTable2',
                'description': 'The second table',
                'price': '201.00'

            }
        ]
        self.assertEqual(expected_data, data)
