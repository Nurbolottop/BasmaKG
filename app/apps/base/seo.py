"""SEO-хелперы: абсолютные URL, canonical/hreflang и разметка schema.org."""
from django.conf import settings
from django.templatetags.static import static
from django.urls import translate_url
from django.utils.html import strip_tags
from django.utils.translation import get_language


def site_root():
    return settings.SITE_URL.rstrip('/')


def absolute(path):
    if not path:
        return ''
    if path.startswith(('http://', 'https://')):
        return path
    return site_root() + path


def strip_lang_prefix(path):
    """'/ky/catalog/' -> '/catalog/' (для поиска ручных SEO-настроек)."""
    for code, _ in settings.LANGUAGES:
        if code != settings.LANGUAGE_CODE and (path == f'/{code}/' or path.startswith(f'/{code}/')):
            return path[len(code) + 1:] or '/'
    return path


def canonical_url(request):
    """Адрес без мусорных параметров (?sort, ?utm, ?q…), но с ?page=N для пагинации."""
    url = absolute(request.path)
    page = request.GET.get('page')
    if page and page.isdigit() and int(page) > 1:
        url += f'?page={page}'
    return url


def alternate_urls(request):
    """hreflang: одна и та же страница на всех языках."""
    urls = []
    for code, name in settings.LANGUAGES:
        urls.append({'code': code, 'name': name, 'url': absolute(translate_url(request.path, code))})
    return urls


def text(value, limit=300):
    value = ' '.join(strip_tags(value or '').split())
    return value[:limit]


# ---------------------------------------------------------------- schema.org

def org_id():
    return site_root() + '/#organization'


def organization_schema(site):
    data = {
        '@context': 'https://schema.org',
        '@type': ['LocalBusiness', 'Store'],
        '@id': org_id(),
        'name': site.site_name,
        'description': site.tagline,
        'url': site_root() + '/',
        'logo': absolute(static('img/logo.png')),
        'image': absolute(static('img/og-default.png')),
        'telephone': site.phone_href,
        'address': {
            '@type': 'PostalAddress',
            'addressLocality': site.city,
            'streetAddress': site.address or site.city,
            'addressCountry': 'KG',
        },
        'areaServed': {'@type': 'Country', 'name': 'Kyrgyzstan'},
        'openingHours': site.opening_hours_schema,
        'priceRange': site.price_range,
        'currenciesAccepted': 'KGS',
        'contactPoint': {
            '@type': 'ContactPoint',
            'telephone': site.phone_href,
            'contactType': 'customer service',
            'availableLanguage': ['ru', 'ky'],
        },
    }
    if site.email:
        data['email'] = site.email
    if site.latitude and site.longitude:
        data['geo'] = {'@type': 'GeoCoordinates', 'latitude': float(site.latitude),
                       'longitude': float(site.longitude)}
    if site.map_link:
        data['hasMap'] = site.map_link
    same_as = [u for u in (site.instagram, site.youtube, site.tiktok, site.facebook) if u]
    if same_as:
        data['sameAs'] = same_as
    return data


def website_schema(site):
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': site_root() + '/#website',
        'url': site_root() + '/',
        'name': site.site_name,
        'inLanguage': ['ru', 'ky'],
        'publisher': {'@id': org_id()},
        'potentialAction': {
            '@type': 'SearchAction',
            'target': {'@type': 'EntryPoint', 'urlTemplate': site_root() + '/catalog/?q={search_term_string}'},
            'query-input': 'required name=search_term_string',
        },
    }


def breadcrumbs_schema(crumbs):
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': c['name'], 'item': absolute(c['url'])}
            for i, c in enumerate(crumbs, 1)
        ],
    }


def faq_schema(faqs):
    faqs = list(faqs)
    if not faqs:
        return None
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [{
            '@type': 'Question',
            'name': f.question,
            'acceptedAnswer': {'@type': 'Answer', 'text': text(f.answer, 1000)},
        } for f in faqs],
    }


def product_schema(product):
    data = {
        '@context': 'https://schema.org',
        '@type': 'Product',
        'name': product.name,
        'description': text(product.short_description or product.description, 500) or product.name,
        'sku': f'BASMA-{product.pk}',
        'url': absolute(product.get_absolute_url()),
        'category': product.category.name,
    }
    if product.cover:
        data['image'] = [absolute(product.cover.url)]
    if product.brand:
        data['brand'] = {'@type': 'Brand', 'name': product.brand}
    if product.price is not None:
        data['offers'] = {
            '@type': 'Offer',
            'url': absolute(product.get_absolute_url()),
            'priceCurrency': 'KGS',
            'price': str(product.price),
            'availability': 'https://schema.org/' + ('InStock' if product.in_stock else 'PreOrder'),
            'itemCondition': 'https://schema.org/NewCondition',
            'seller': {'@id': org_id()},
        }
    return data


def item_list_schema(objects, name):
    return {
        '@context': 'https://schema.org',
        '@type': 'ItemList',
        'name': name,
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'url': absolute(o.get_absolute_url()), 'name': str(o)}
            for i, o in enumerate(objects, 1)
        ],
    }


def service_schema(service, site):
    data = {
        '@context': 'https://schema.org',
        '@type': 'Service',
        'name': service.name,
        'serviceType': service.name,
        'description': text(service.short_description or service.description, 500),
        'url': absolute(service.get_absolute_url()),
        'provider': {'@id': org_id()},
        'areaServed': {'@type': 'City', 'name': site.city},
        'inLanguage': get_language(),
    }
    if service.image:
        data['image'] = absolute(service.image.url)
    return data
