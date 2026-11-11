from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from modeltranslation.admin import TabbedTranslationAdmin as TA

from apps.base.models import SeoMeta, SiteSettings

admin.site.site_header = 'Basma Service — управление сайтом'
admin.site.site_title = 'Basma Service'
admin.site.index_title = 'Разделы'


@admin.register(SiteSettings)
class SiteSettingsAdmin(TA):
    fieldsets = [
        ('Бренд и первый экран', {'fields': ['site_name', 'tagline', 'hero_title', 'hero_text']}),
        ('Цифры на главной', {'fields': [('stat_years', 'stat_clients', 'stat_speed')]}),
        ('Контакты', {'fields': [('phone', 'phone_2'), ('whatsapp', 'telegram'), 'email',
                                 'city', 'address', 'working_hours', 'map_link', 'map_embed_url']}),
        ('Для поисковиков (карточка организации)', {'fields': [('latitude', 'longitude'), 'opening_hours_schema',
                                                               'price_range']}),
        ('Соцсети', {'fields': ['instagram', 'youtube', 'tiktok', 'facebook']}),
        ('SEO главной', {'fields': ['meta_title', 'meta_description', 'og_image', 'seo_text']}),
        ('Вебмастера и аналитика', {'fields': [('google_verification', 'yandex_verification'),
                                               ('ga4_id', 'ym_id'), 'head_scripts']}),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(reverse('admin:base_sitesettings_change', args=[obj.pk]))


@admin.register(SeoMeta)
class SeoMetaAdmin(TA):
    list_display = ['path', 'title', 'noindex']
    list_filter = ['noindex']
    search_fields = ['path', 'title']
    fields = ['path', 'title', 'description', 'og_image', 'noindex']
