from rest_framework.serializers import ModelSerializer
from versatileimagefield.serializers import VersatileImageFieldSerializer

from store.models import Product, Category, ProductImage


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class ProductImageSerializer(ModelSerializer):
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


class ProductSerializer(ModelSerializer):
    category = CategorySerializer()
    images = ProductImageSerializer(source='productimage_set', many=True)

    class Meta:
        model = Product
        fields = '__all__'
