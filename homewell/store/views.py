from django.contrib.auth import logout
from django.db.models import Count, Case, When, Avg
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, CharFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from store.models import Product, UserProductRelation
from store.permissions import IsStaffOrReadOnly
from store.serializers import ProductSerializer, UserProductRelationSerializer


class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name='price', lookup_expr='gte')
    max_price = NumberFilter(field_name='price', lookup_expr='lte')
    category = CharFilter(field_name='category__slug', lookup_expr='exact')

    class Meta:
        model = Product
        fields = ['min_price', 'max_price', 'category']


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all().annotate(
        in_favorite_ann=Count(Case(When(userproductrelation__in_favorites=True, then=1)))
    ).select_related('category').prefetch_related('images')  #,rating_ann=Avg('userproductrelation__rate')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    permission_classes = [IsStaffOrReadOnly]
    search_fields = ['name']
    ordering_fields = ['price', 'rating']
    lookup_field = 'slug'


class UserProductRelationViewSet(UpdateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    queryset = UserProductRelation.objects.all()
    serializer_class = UserProductRelationSerializer
    lookup_field = 'product'

    def get_object(self):
        obj, _ = UserProductRelation.objects.get_or_create(user=self.request.user,
                                                           product_id=self.kwargs['product'])
        # _ це створений чи ні
        return obj


def google_auth(request):
    return render(request, 'oauth.html')


def logout_view(request):
    logout(request)
