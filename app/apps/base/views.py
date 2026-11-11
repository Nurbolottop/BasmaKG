from django.conf import settings
from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render
from django.views.decorators.http import require_GET

from apps.base import seo
from apps.catalog.models import Category, Product
from apps.cms.models import FAQ, Advantage, Review, Service, Step


def home(request):
    faqs = FAQ.objects.filter(is_active=True)[:6]
    services = Service.objects.filter(is_active=True)
    return render(request, 'base/home.html', {
        'services': services,
        'categories': Category.objects.filter(is_active=True),
        'popular': Product.objects.active().filter(is_popular=True).select_related('category')[:8],
        'advantages': Advantage.objects.filter(is_active=True),
        'steps': Step.objects.all(),
        'reviews': Review.objects.filter(is_active=True)[:8],
        'faqs': faqs,
        'schema': [seo.faq_schema(faqs)],
    })


@require_GET
def robots_txt(request):
    root = settings.SITE_URL.rstrip('/')
    lines = [
        'User-agent: *',
        'Disallow: /ckeditor/',
        'Disallow: /lead/',
        'Disallow: /ky/lead/',
        'Disallow: /thanks/',
        'Disallow: /ky/thanks/',
        'Disallow: /media/leads/',
        'Allow: /',
        '',
        '# Яндекс: параметры, не меняющие содержимое страницы',
        'User-agent: Yandex',
        'Disallow: /ckeditor/',
        'Disallow: /lead/',
        'Disallow: /ky/lead/',
        'Disallow: /thanks/',
        'Disallow: /ky/thanks/',
        'Disallow: /media/leads/',
        'Clean-param: sort&holder&utm_source&utm_medium&utm_campaign&utm_content&utm_term&gclid&fbclid&yclid',
        'Allow: /',
        '',
        f'Sitemap: {root}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines) + '\n', content_type='text/plain; charset=utf-8')


def error_404(request, exception):
    return render(request, '404.html', {'noindex': True}, status=404)


def error_500(request):
    return render(request, '500.html', status=500)


def favicon(request):
    return HttpResponsePermanentRedirect(staticfiles_storage.url('img/favicon.ico'))
