from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.base import seo
from apps.base.models import SiteSettings
from apps.cms.models import FAQ, Advantage, Page, Review, Service, Step


def _home():
    return {'name': _('Главная'), 'url': reverse('base:home')}


def services(request):
    items = Service.objects.filter(is_active=True)
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, 'cms/services.html', {
        'services': items,
        'steps': Step.objects.all(),
        'faqs': faqs,
        'breadcrumbs': [_home(), {'name': _('Услуги'), 'url': reverse('cms:services')}],
        'schema': [seo.item_list_schema(items, _('Услуги')), seo.faq_schema(faqs)],
    })


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    return render(request, 'cms/service.html', {
        'service': service,
        'others': Service.objects.filter(is_active=True).exclude(pk=service.pk),
        'steps': Step.objects.all(),
        'breadcrumbs': [_home(), {'name': _('Услуги'), 'url': reverse('cms:services')},
                        {'name': service.name, 'url': service.get_absolute_url()}],
        'schema': [seo.service_schema(service, SiteSettings.load())],
        'og_image': seo.absolute(service.image.url) if service.image else None,
    })


def about(request):
    page = Page.objects.filter(slug='about', is_active=True).first()
    return render(request, 'cms/about.html', {
        'page': page,
        'advantages': Advantage.objects.filter(is_active=True),
        'reviews': Review.objects.filter(is_active=True)[:6],
        'steps': Step.objects.all(),
        'breadcrumbs': [_home(), {'name': _('О компании'), 'url': reverse('cms:about')}],
        'schema': [{'@context': 'https://schema.org', '@type': 'AboutPage',
                    'url': seo.absolute(reverse('cms:about')), 'about': {'@id': seo.org_id()}}],
    })


def page(request, slug):
    obj = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, 'cms/page.html', {
        'page': obj,
        'breadcrumbs': [_home(), {'name': obj.title, 'url': obj.get_absolute_url()}],
    })
