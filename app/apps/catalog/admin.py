from django.contrib import admin
from django.utils.html import format_html
from modeltranslation.admin import TabbedTranslationAdmin as TA

from apps.catalog.models import Category, Product, ProductImage


def thumb(image, size=48):
    if not image:
        return '—'
    return format_html('<img src="{}" style="width:{}px;height:{}px;object-fit:contain;'
                       'background:#f4f4f5;border-radius:8px">', image.url, size, size)


@admin.register(Category)
class CategoryAdmin(TA):
    list_display = ['preview', 'name', 'tagline', 'order', 'is_active', 'products_count']
    list_display_links = ['preview', 'name']
    list_editable = ['order', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {}
    fieldsets = [
        (None, {'fields': ['name', 'slug', 'tagline', 'image', 'description', 'order', 'is_active']}),
        ('SEO', {'fields': ['meta_title', 'meta_description', 'seo_text'], 'classes': ['collapse']}),
    ]

    @admin.display(description='')
    def preview(self, obj):
        return thumb(obj.image)

    @admin.display(description='Товаров')
    def products_count(self, obj):
        return obj.products.count()


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order']


@admin.register(Product)
class ProductAdmin(TA):
    list_display = ['preview', 'name', 'category', 'price', 'in_stock', 'is_popular',
                    'in_constructor', 'is_active', 'order']
    list_display_links = ['preview', 'name']
    list_editable = ['price', 'in_stock', 'is_popular', 'in_constructor', 'is_active', 'order']
    list_filter = ['category', 'is_active', 'in_stock', 'is_popular', 'in_constructor', 'shape']
    search_fields = ['name', 'brand', 'short_description']
    autocomplete_fields = ['category']
    inlines = [ProductImageInline]
    fieldsets = [
        (None, {'fields': ['category', 'name', 'slug', 'short_description', 'image', 'description']}),
        ('Цена и наличие', {'fields': [('price', 'price_from', 'old_price'), ('in_stock', 'is_popular', 'is_active'), 'order']}),
        ('Характеристики', {'fields': [('brand', 'size', 'shape'), 'in_constructor']}),
        ('SEO', {'fields': ['meta_title', 'meta_description'], 'classes': ['collapse']}),
    ]

    @admin.display(description='')
    def preview(self, obj):
        return thumb(obj.cover)
