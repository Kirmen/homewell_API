from rest_framework.fields import SerializerMethodField
from rest_framework.relations import SlugRelatedField
from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from store.models import Product, Category, ProductImage, UserProductRelation, UserProfile, Address, OrderItem, Order


# class CategorySerializer(ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

    image = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
            ('medium_square_crop', 'crop__400x400'),
            ('small_square_crop', 'crop__50x50')
        ]
    )


class ProductSerializer(serializers.ModelSerializer):
    in_favorite_ann = serializers.IntegerField(read_only=True)

    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    # category = CategorySerializer()  щоб одразу давати всі данні про категорію
    images = ProductImageSerializer(many=True)

    class Meta:
        model = Product
        fields = (
            'id', 'name', 'slug', 'category', 'description', 'price', 'rating', 'images', 'quantity',
            'in_favorite_ann')  # , 'favorites_by'

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)

        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)

        return product

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.description)

        instance.category = validated_data.get('category', instance.category)

        images_data = validated_data.pop('images', [])
        for image_data in images_data:
            image_instance = instance.productimage_set.get(id=image_data.get('id', None))
            image_instance.image = image_data.get('image', image_instance.image)

            image_instance.save()

        instance.save()
        return instance


class UserProductRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProductRelation
        fields = ('product', 'rate', 'in_favorites')


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    fav_prod = SerializerMethodField()
    # orders = OrderSerializer(many=True)
    addresses = AddressSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'fav_prod', 'orders', 'addresses')

    def get_fav_prod(self, instance):
        user = instance.user
        favorite_products = Product.objects.filter(userproductrelation__user=user,
                                                   userproductrelation__in_favorites=True)
        serialized_favorite_products = ProductSerializer(favorite_products,
                                                         many=True).data  # треба спец серіалізатор для продуктів, бо багато інфи
        return serialized_favorite_products


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Product.objects.all()
    )
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = '__all__'
