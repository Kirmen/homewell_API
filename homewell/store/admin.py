from django.contrib import admin
from .models import Product, Category, ProductImage, UserProductRelation, UserProfile, Order, OrderItem, Address


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True
    list_display = ('id', 'name', 'slug', 'category')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('category',)
    readonly_fields = ('rating',)


admin.site.register(ProductImage)
admin.site.register(UserProductRelation)
admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)
