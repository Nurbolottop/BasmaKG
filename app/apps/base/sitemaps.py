from urllib.parse import urljoin, urlsplit

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.catalog.models import Category, Product
from apps.cms.models import Page, Service

PROTOCOL = urlsplit(settings.SITE_URL).scheme or 'https'


class BaseSitemap(Sitemap):
    """Оба языка (ru + /ky/) с hreflang-ссылками и картинками."""
    i18n = True
    alternates = True
    x_default = True
    protocol = PROTOCOL

    def lastmod(self, item):
        return getattr(item, 'updated_at', None)

    def get_domain(self, site=None):
        # всегда основной домен из SITE_URL, а не Host запроса
        return urlsplit(settings.SITE_URL).netloc or super().get_domain(site)

    def get_urls(self, *args, **kwargs):
        urls = super().get_urls(*args, **kwargs)
        for u in urls:
            item = u['item']
            if isinstance(item, tuple):  # при i18n=True Django отдаёт (объект, язык)
                item = item[0]
            image = getattr(item, 'sitemap_image', None)
            if image:
                u['image'] = urljoin(u['location'], image)
        return urls


class StaticSitemap(BaseSitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['base:home', 'catalog:catalog', 'catalog:constructor', 'cms:services',
                'cms:about', 'contacts:contacts']

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == 'base:home' else 0.8


class CategorySitemap(BaseSitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return Category.objects.filter(is_active=True)


class ProductSitemap(BaseSitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return Product.objects.active().select_related('category')


class ServiceSitemap(BaseSitemap):
    priority = 0.9
    changefreq = 'monthly'

    def items(self):
        return Service.objects.filter(is_active=True)


class PageSitemap(BaseSitemap):
    priority = 0.3
    changefreq = 'yearly'

    def items(self):
        return Page.objects.filter(is_active=True).exclude(slug='about')


sitemaps = {
    'static': StaticSitemap,
    'categories': CategorySitemap,
    'products': ProductSitemap,
    'services': ServiceSitemap,
    'pages': PageSitemap,
}
