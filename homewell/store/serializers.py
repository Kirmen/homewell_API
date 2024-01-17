from rest_framework.serializers import ModelSerializer

from store.models import Product, Category


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class ProductSerializer(ModelSerializer):
    category = CategorySerializer()
    class Meta:
        model = Product
        fields = '__all__'