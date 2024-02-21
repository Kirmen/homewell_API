from collections import OrderedDict

from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Category, Product, UserProductRelation
from store.serializers import ProductSerializer


class ProductSerializerTestCase(TestCase):
    def test_ok(self):
        user1 = User.objects.create_user(
            username='user1', password='user1_password'
        )
        user2 = User.objects.create_user(
            username='user2', password='user2_password'
        )
        user3 = User.objects.create_user(
            username='user3', password='user3_password'
        )
        category1 = Category.objects.create(name='Kitchen', slug='kitchen')
        product1 = Product.objects.create(name='SuperTable', slug='supertable', category=category1,
                                          description='The best table',
                                          price=200)
        product2 = Product.objects.create(name='SuperTable2', slug='supertable2', category=category1,
                                          description='The second table',
                                          price=201, quantity=10)

        UserProductRelation.objects.create(user=user1, product=product1, in_favorites=True, rate=5)
        UserProductRelation.objects.create(user=user2, product=product1, in_favorites=True, rate=4)
        UserProductRelation.objects.create(user=user3, product=product1, in_favorites=True)

        UserProductRelation.objects.create(user=user1, product=product2, in_favorites=True, rate=5)
        UserProductRelation.objects.create(user=user2, product=product2, in_favorites=True, rate=3)
        UserProductRelation.objects.create(user=user3, product=product2, in_favorites=False, rate=4)

        products = Product.objects.all().annotate(
            in_favorite_ann=Count(Case(When(userproductrelation__in_favorites=True, then=1))),
            rating_ann=Avg('userproductrelation__rate')
        ).order_by('id')

        data = ProductSerializer(products, many=True).data
        expected_data = [
            {
                'id': product1.id,
                'name': 'SuperTable',
                "slug": "supertable",
                'category': "kitchen",
                'description': 'The best table',
                'price': '200.00',
                'rating_ann': '4.50',
                'images': [],
                "quantity": 0,
                'in_favorite_ann': 3

            },
            {
                'id': product2.id,
                'name': 'SuperTable2',
                "slug": "supertable2",
                'category': "kitchen",
                'description': 'The second table',
                'price': '201.00',
                'rating_ann': '4.00',
                'images': [],
                "quantity": 10,
                'in_favorite_ann': 2

            }
        ]
        self.assertEqual(expected_data, data)
