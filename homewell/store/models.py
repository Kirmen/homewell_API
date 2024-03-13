from django.db import models
from django.contrib.auth.models import User
from versatileimagefield.fields import VersatileImageField


class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50,
                            verbose_name='Url',
                            unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=50,
                            verbose_name='Url',
                            unique=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 related_name='product', null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=None, null=True)
    quantity = models.PositiveIntegerField(default=0)
    favorites_by = models.ManyToManyField(User, through='UserProductRelation',
                                          related_name='favorite_products')

    def __str__(self):
        return self.slug


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
    title = models.CharField(max_length=200, null=True, blank=True)
    image = VersatileImageField(null=True, blank=True, upload_to=f'images/')

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"

    def __str__(self):
        res = ''
        if self.title:
            res = self.title
        else:
            res = self.image.url
        return res


class UserProductRelation(models.Model):
    RATE_CHOICES = (
        (1, 'OK'),
        (2, 'Fine'),
        (3, 'Good'),
        (4, 'Amazing'),
        (5, 'Super'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rate = models.PositiveSmallIntegerField(choices=RATE_CHOICES, null=True)
    in_favorites = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username}, product: {self.product.name}, rate: {self.rate}'

    def save(self, *args, **kwargs):
        from store.logic_operations import set_rating

        creating = not self.pk
        old_rating = self.rate

        super().save(*args, **kwargs)

        new_rating = self.rate
        if old_rating != new_rating or creating:
            set_rating(self.product)


class Address(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    city = models.CharField(max_length=255)
    carrier_choices = [
        ('carrier1', 'NovaPost'),
        ('carrier2', 'UkrPost'),
    ]
    carrier = models.CharField(max_length=20, choices=carrier_choices)
    branch = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"UserId: {self.user_profile.user.id}, {self.get_carrier_display()}:{self.branch}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.user_profile.addresses.add(self)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    orders = models.ManyToManyField('Order', related_name='user_orders')
    addresses = models.ManyToManyField(Address, related_name='user_addresses')

    def __str__(self):
        return f'user ID = {self.user.id}'


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)

    def total_price(self):
        return self.product.price * self.quantity

    # def save(self, *args, **kwargs):
    #     super(OrderItem, self).save(*args, **kwargs)
    #     self.product.quantity -= self.quantity
    #     self.product.save()

    def __str__(self):
        return f'P: {self.product}, Q: {self.quantity}'


class Order(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('new', 'New'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    order_items = models.ManyToManyField(OrderItem, related_name='ordered_items')
    # можливо видалити тут айтемс і в серіалізаторі іх
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'userID: {self.user_profile.user.id}, orderID: {self.id}'

    # def save(self, *args, **kwargs):
    #     super(Order, self).save(*args, **kwargs)
    #     self.total_amount = sum(item.total_price() for item in self.order_items.all())
    #     if self.status == 'canceled':
    #         for item in self.order_items.all():
    #             item.product.quantity += item.quantity
    #             item.product.save()
    #     self.user_profile.orders.add(self)

    def save(self, *args, **kwargs):
        # if not self.id:
        #     for item in self.order_items.all():
        #         item.product.quantity -= item.quantity
        #         item.product.save()
        #     super(Order, self).save(*args, **kwargs)

        self.total_amount = sum(item.total_price() for item in self.order_items.all())

        super(Order, self).save(*args, **kwargs)

        # if self.status == 'canceled':
        #     for item in self.order_items.all():
        #         item.product.quantity += item.quantity
        #         item.product.save()
        #
        # self.user_profile.orders.add(self)
