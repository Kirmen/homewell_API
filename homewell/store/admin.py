from django.contrib import admin
from .models import Product, Category, ProductImage


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('id', 'name', 'slug')
    list_display_links = ('id', 'name')


class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True
    list_display = ('id', 'name', 'slug', 'category')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('category',)
    readonly_fields = ('rating',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(ProductImage)
