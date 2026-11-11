from django.templatetags.static import static

from apps.base import seo
from apps.base.js_i18n import js_strings
from apps.base.models import SeoMeta, SiteSettings
from apps.catalog.models import Category
from apps.cms.models import Service


def site(request):
    settings_obj = SiteSettings.load()
    seo_meta = SeoMeta.for_path(seo.strip_lang_prefix(request.path))
    og_default = settings_obj.og_image.url if settings_obj.og_image else static('img/og-default.png')
    return {
        'site': settings_obj,
        'nav_categories': Category.objects.filter(is_active=True),
        'nav_services': Service.objects.filter(is_active=True),
        'seo_meta': seo_meta,
        'canonical_url': seo.canonical_url(request),
        'alternate_urls': seo.alternate_urls(request),
        'site_root': seo.site_root(),
        'og_image_default': seo.absolute(og_default),
        'org_schema': seo.organization_schema(settings_obj),
        'website_schema': seo.website_schema(settings_obj),
        'js_i18n': js_strings(),
    }
