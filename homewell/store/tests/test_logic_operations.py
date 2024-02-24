from django.contrib.auth.models import User
from django.test import TestCase

from store.logic_operations import set_rating
from store.models import Category, Product, UserProductRelation


class SetRatingTestCase(TestCase):
    def setUp(self) -> None:
        self.user1 = User.objects.create_user(username='user1', password='user1_password')
        self.user2 = User.objects.create_user(
            username='user2',
            password='user2_password')

        category1 = Category.objects.create(name='Kitchen', slug='kitchen')
        self.product1 = Product.objects.create(name='Super Table', slug='super-table', category=category1,
                                               description='The best table',
                                               price=200)

        UserProductRelation.objects.create(user=self.user1, product=self.product1, in_favorites=True, rate=5)
        UserProductRelation.objects.create(user=self.user2, product=self.product1, in_favorites=True, rate=4)

    def test_ok(self):
        set_rating(self.product1)
        self.assertEqual(self.product1.rating, 4.50)
