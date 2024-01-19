from collections import OrderedDict

from django.test import TestCase

from store.models import Category, Product
from store.serializers import ProductSerializer


class ProductSerializerTestCase(TestCase):
    def test_ok(self):
        category1 = Category.objects.create(name='Kitchen', slug='kitchen')
        product1 = Product.objects.create(name='SuperTable', slug='supertable', category=category1,
                                          description='The best table',
                                          price=200)
        product2 = Product.objects.create(name='SuperTable2', slug='supertable2', category=category1,
                                          description='The second table',
                                          price=201, quantity=10)
        data = ProductSerializer([product1, product2], many=True).data

        expected_data = [
            {
                'id': product1.id,
                'category': 'Kitchen',
                'images': [],
                'name': 'SuperTable',
                "slug": "supertable",
                'description': 'The best table',
                'price': '200.00',
                "rating": "0.00",
                "quantity": 0

            },
            {
                'id': product2.id,
                'category': 'Kitchen',
                'images': [],
                'name': 'SuperTable2',
                "slug": "supertable2",
                'description': 'The second table',
                'price': '201.00',
                "rating": "0.00",
                "quantity": 10

            }
        ]
        self.assertEqual(expected_data, data)
