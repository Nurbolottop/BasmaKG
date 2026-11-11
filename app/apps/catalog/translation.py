from modeltranslation.translator import TranslationOptions, register

from apps.catalog.models import Category, Product


@register(Category)
class CategoryTR(TranslationOptions):
    fields = ('name', 'tagline', 'description', 'seo_text', 'meta_title', 'meta_description')


@register(Product)
class ProductTR(TranslationOptions):
    fields = ('name', 'short_description', 'description', 'meta_title', 'meta_description')
