import json
import os

import django
from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When, Avg
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test.utils import CaptureQueriesContext

from store.models import Product, Category, UserProductRelation
from store.serializers import ProductSerializer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homewell.settings')
if not settings.configured:
    django.setup()


class HomewellApiTestCase(APITestCase):
    def setUp(self) -> None:
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin_password',
            is_staff=True,
            is_superuser=False
        )
        self.not_admin_user = User.objects.create_user(
            username='not_admin',
            password='not_admin_password',
            is_staff=False,
            is_superuser=False
        )
        category1 = Category.objects.create(name='Kitchen', slug='kitchen')
        category2 = Category.objects.create(name='Living room', slug='living-room')
        self.product1 = Product.objects.create(name='Super Table', slug='super-table', category=category1,
                                               description='The best table',
                                               price=200)
        UserProductRelation.objects.create(user=self.not_admin_user, product=self.product1, in_favorites=True, rate=5)

        self.product2 = Product.objects.create(name='Super Table2', slug='super-table2', category=category1,
                                               description='The second table',
                                               price=201, quantity=10)
        self.product3 = Product.objects.create(name='Super Sofa', slug='super-sofa', category=category2,
                                               description='The best sofa',
                                               price=202, quantity=15)

    def test_check_annotate(self):
        products = Product.objects.all().annotate(
            in_favorite_ann=Count(Case(When(userproductrelation__in_favorites=True, then=1))),
            rating_ann=Avg('userproductrelation__rate')
        ).order_by('id')

        serializer_data = ProductSerializer(products, many=True).data
        self.assertEqual(serializer_data[0]['in_favorite_ann'], 1)

    def test_check_related_and_prefetch(self):
        url = reverse('product-list')
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))

    def test_get(self):
        url = reverse('product-list')
        response = self.client.get(url)

        products = Product.objects.all().annotate(
            in_favorite_ann=Count(Case(When(userproductrelation__in_favorites=True, then=1)))
        )
        print(response.data)
        serializer_data = ProductSerializer(products, many=True).data
        print(serializer_data)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_price_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'min_price': 200, 'max_price': 201})

        products = Product.objects.filter(id__in=[self.product1.id, self.product2.id]).annotate(
            in_favorite_ann=Count(Case(When(userproductrelation__in_favorites=True, then=1)))
        ).order_by('id')
        serializer_data = ProductSerializer(products, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_category_filter(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'category': 'living-room'})

        product = Product.objects.filter(id__in=[self.product3.id]).annotate(
            in_favorite_ann=Count(Case(When(userproductrelation__in_favorites=True, then=1)))
        )

        serializer_data = ProductSerializer(product, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_search(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'search': 'super sofa'})
        product = Product.objects.filter(id__in=[self.product3.id]).annotate(
            in_favorite_ann=Count(Case(When(userproductrelation__in_favorites=True, then=1)))
        )

        serializer_data = ProductSerializer(product, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_get_sort(self):
        url = reverse('product-list')
        response = self.client.get(url, data={'ordering': '-price'})
        products = Product.objects.all().annotate(
            in_favorite_ann=Count(Case(When(userproductrelation__in_favorites=True, then=1)))
        ).order_by('-price')

        serializer_data = ProductSerializer(products, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-list')
        data = {
            "category": "living-room",
            "images": [],
            "name": "Sofa 2",
            "slug": "sofa-2",
            "description": "sofa 2 description",
            "price": 260
        }
        json_data = json.dumps(data)
        self.client.force_login(self.admin_user)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Product.objects.all().count())

    def test_create_not_admin(self):
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-list')
        data = {
            "category": "living-room",
            "images": [],
            "name": "Sofa 2",
            "slug": "sofa-2",
            "description": "sofa 2 description",
            "price": 260
        }
        json_data = json.dumps(data)
        self.client.force_login(self.not_admin_user)
        response = self.client.post(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Product.objects.all().count())

    def test_update(self):
        url = reverse('product-detail', args=(self.product1.slug,))
        data = {
            "category": self.product1.category.slug,
            "images": [],
            "name": self.product1.name,
            "slug": self.product1.slug,
            "description": self.product1.description,
            "price": 260
        }
        json_data = json.dumps(data)
        self.client.force_login(self.admin_user)
        response = self.client.put(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.product1.refresh_from_db()
        self.assertEqual(260, self.product1.price)

    def test_delete(self):
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-detail', args=(self.product1.slug,))
        self.client.force_login(self.admin_user)
        response = self.client.delete(url, content_type='application/json')

        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Product.objects.all().count())

    def test_delete_not_admin(self):
        self.assertEqual(3, Product.objects.all().count())
        url = reverse('product-detail', args=(self.product1.slug,))
        self.client.force_login(self.not_admin_user)
        response = self.client.delete(url, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(3, Product.objects.all().count())


class UserProductTestCase(APITestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(
            username='user1', password='user1_password'
        )
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

    def test_in_favorites(self):
        url = reverse('userproductrelation-detail', args=(self.product1.id,))
        data = {
            'in_favorites': True
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user1)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # self.product1.refresh_from_db()
        relation = UserProductRelation.objects.get(user=self.user1, product=self.product1)
        self.assertTrue(relation.in_favorites)

    def test_in_favorites_not_auth(self):
        url = reverse('userproductrelation-detail', args=(self.product1.id,))
        data = {
            'in_favorites': True
        }
        json_data = json.dumps(data)

        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_rate(self):
        url = reverse('userproductrelation-detail', args=(self.product1.id,))
        data = {
            'rate': 5
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user1)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserProductRelation.objects.get(user=self.user1, product=self.product1)
        self.assertTrue(5, relation.rate)

    def test_rate_wrong(self):
        url = reverse('userproductrelation-detail', args=(self.product1.id,))
        data = {
            'rate': 6
        }
        json_data = json.dumps(data)

        self.client.force_login(self.user1)
        response = self.client.patch(url, data=json_data, content_type='application/json')

        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
