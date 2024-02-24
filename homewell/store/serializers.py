from rest_framework.relations import SlugRelatedField
from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer

from store.models import Product, Category, ProductImage, UserProductRelation


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
