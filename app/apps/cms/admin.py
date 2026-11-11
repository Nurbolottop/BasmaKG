from django.contrib import admin
from modeltranslation.admin import TabbedTranslationAdmin as TA

from apps.cms.models import FAQ, Advantage, Page, Review, Service, Step

SEO = ('SEO', {'fields': ['meta_title', 'meta_description'], 'classes': ['collapse']})


@admin.register(Service)
class ServiceAdmin(TA):
    list_display = ['name', 'price_text', 'term_text', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name']
    fieldsets = [
        (None, {'fields': ['name', 'slug', 'icon', 'short_description', 'image']}),
        ('Подробно', {'fields': [('price_text', 'term_text'), 'features', 'description']}),
        ('Публикация', {'fields': ['order', 'is_active']}),
        SEO,
    ]


@admin.register(Advantage)
class AdvantageAdmin(TA):
    list_display = ['title', 'text', 'icon', 'order', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(Step)
class StepAdmin(TA):
    list_display = ['title', 'text', 'order']
    list_editable = ['order']


@admin.register(FAQ)
class FAQAdmin(TA):
    list_display = ['question', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['question', 'answer']


@admin.register(Review)
class ReviewAdmin(TA):
    list_display = ['name', 'company', 'rating', 'order', 'is_active']
    list_editable = ['order', 'is_active']


@admin.register(Page)
class PageAdmin(TA):
    list_display = ['title', 'slug', 'is_active']
    prepopulated_fields = {}
    fieldsets = [(None, {'fields': ['title', 'slug', 'lead', 'content', 'is_active']}), SEO]
