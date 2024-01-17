from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'



class Product(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    photos = models.ImageField(upload_to='product_photos/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)


    # rating = models.FloatField(default=0.0)
    # quantity = models.PositiveIntegerField(default=0)
    #
    # def update_rating(self, new_rating, rating_id=None):
    #     if 1 <= new_rating <= 5:
    #         ratings_aggregate = UserRating.objects.filter(product=self).aggregate(
    #             total_rating=Avg('rating'),
    #             total_ratings=models.Count('rating')
    #         )
    #
    #         total_rating = ratings_aggregate['total_rating'] or 0.0
    #         total_ratings = ratings_aggregate['total_ratings'] or 1
    #
    #         if rating_id:
    #             old_rating = UserRating.objects.get(id=rating_id).rating
    #             total_rating -= old_rating
    #
    #         self.rating = total_rating / total_ratings
    #         self.save()
    #     else:
    #         raise ValueError("Рейтинг повинен бути від 1 до 5.")
    #
    # def update_quantity(self, quantity_to_reduce):
    #     if self.quantity >= quantity_to_reduce:
    #         self.quantity -= quantity_to_reduce
    #         self.save()
    #         return True
    #     return False


# class Address(models.Model):
#     city = models.CharField(max_length=255)
#     carrier_choices = [
#         ('carrier1', 'Nova Post'),
#         ('carrier2', 'Ukr Post'),
#     ]
#     carrier = models.CharField(max_length=20, choices=carrier_choices)
#     branch = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     first_name = models.CharField(max_length=255)
#     phone_number = models.CharField(max_length=20)
#
#     def __str__(self):
#         return f"{self.first_name} {self.last_name}, {self.city}"
#
#
# class UserRating(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     rating = models.FloatField(default=0.0)
#
#     def save(self, *args, **kwargs):
#         ratings_for_product = UserRating.objects.filter(product=self.product)
#         total_rating = sum([rating.rating for rating in ratings_for_product])
#         self.product.rating = total_rating / max(len(ratings_for_product), 1)
#         self.product.save()
#
#         super(UserRating, self).save(*args, **kwargs)
#
#
# class UserProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     email = models.EmailField(unique=True)
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     addresses = models.ManyToManyField(Address, related_name='user_addresses', blank=True)
#     favorites = models.ManyToManyField(Product, related_name='favorited_by', blank=True)
#     orders = models.ManyToManyField('Order', related_name='customer_orders', blank=True)
#
#
# class OrderItem(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)
#
#     def save(self, *args, **kwargs):
#         super(OrderItem, self).save(*args, **kwargs)
#
#     def total_price(self):
#         return self.product.price * self.quantity
#
#
# class Order(models.Model):
#     user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
#     address = models.ForeignKey(Address, on_delete=models.CASCADE)
#     STATUS_CHOICES = [
#         ('new', 'New'),
#         ('confirmed', 'Confirmed'),
#         ('completed', 'Completed'),
#     ]
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
#     order_items = models.ManyToManyField(OrderItem, related_name='ordered_items')
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#
#     def save(self, *args, **kwargs):
#         self.total_amount = sum(item.total_price for item in self.order_items.all())
#         super(Order, self).save(*args, **kwargs)