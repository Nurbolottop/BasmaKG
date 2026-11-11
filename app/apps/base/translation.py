from modeltranslation.translator import TranslationOptions, register

from apps.base.models import SeoMeta, SiteSettings


@register(SiteSettings)
class SiteSettingsTR(TranslationOptions):
    fields = ('tagline', 'hero_title', 'hero_text', 'city', 'address', 'working_hours', 'price_range',
              'meta_title', 'meta_description', 'seo_text')


@register(SeoMeta)
class SeoMetaTR(TranslationOptions):
    fields = ('title', 'description')
