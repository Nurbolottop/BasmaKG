from django.core.paginator import Paginator
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.base import seo
from apps.catalog.models import Category, Product
from apps.cms.models import FAQ

SORTS = {
    'popular': ['-is_popular', 'order', '-created_at'],
    'price': [F('price').asc(nulls_last=True)],
    '-price': [F('price').desc(nulls_last=True)],
    'new': ['-created_at'],
}


def catalog(request, slug=None):
    categories = Category.objects.filter(is_active=True)
    category = get_object_or_404(categories, slug=slug) if slug else None

    products = Product.objects.active().select_related('category')
    if category:
        products = products.filter(category=category)

    q = request.GET.get('q', '').strip()[:100]
    if q:
        # Ищем по обоим языкам, чтобы «Trodat» и кыргызские названия находились везде
        products = products.filter(
            Q(name_ru__icontains=q) | Q(name_ky__icontains=q) | Q(brand__icontains=q)
            | Q(short_description_ru__icontains=q) | Q(short_description_ky__icontains=q)
            | Q(category__name_ru__icontains=q) | Q(category__name_ky__icontains=q)
        )

    sort = request.GET.get('sort', 'popular')
    products = products.order_by(*SORTS.get(sort, SORTS['popular']))

    page = Paginator(products, 24).get_page(request.GET.get('page'))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'catalog/_grid.html', {'page': page, 'q': q, 'sort': sort})

    crumbs = [{'name': _('Главная'), 'url': reverse('base:home')},
              {'name': _('Каталог'), 'url': reverse('catalog:catalog')}]
    if category:
        crumbs.append({'name': category.name, 'url': category.get_absolute_url()})

    return render(request, 'catalog/catalog.html', {
        'categories': categories,
        'category': category,
        'page': page,
        'q': q,
        'sort': sort,
        'breadcrumbs': crumbs,
        # страницы поиска не индексируем — это дубли каталога
        'noindex': bool(q),
        'schema': [seo.item_list_schema(page.object_list, category.name if category else _('Каталог'))],
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.active().select_related('category').prefetch_related('images'), slug=slug)
    related = Product.objects.active().filter(category=product.category).exclude(pk=product.pk)[:4]
    return render(request, 'catalog/product.html', {
        'product': product,
        'related': related,
        'breadcrumbs': [
            {'name': _('Главная'), 'url': reverse('base:home')},
            {'name': _('Каталог'), 'url': reverse('catalog:catalog')},
            {'name': product.category.name, 'url': product.category.get_absolute_url()},
            {'name': product.name, 'url': product.get_absolute_url()},
        ],
        'schema': [seo.product_schema(product)],
        'og_type': 'product',
        'og_image': seo.absolute(product.cover.url) if product.cover else None,
    })


def constructor(request):
    holders = Product.objects.active().filter(in_constructor=True).select_related('category')
    holders_data = [{
        'id': p.pk,
        'name': p.name,
        'brand': p.brand,
        'size': p.size,
        'shape': p.shape,
        'price': int(p.price) if p.price is not None else None,
        'image': p.cover.url if p.cover else '',
        'category': p.category.name,
    } for p in holders]
    faqs = FAQ.objects.filter(is_active=True)[:5]
    return render(request, 'catalog/constructor.html', {
        'holders_data': holders_data,
        'faqs': faqs,
        'breadcrumbs': [
            {'name': _('Главная'), 'url': reverse('base:home')},
            {'name': _('Конструктор печати'), 'url': reverse('catalog:constructor')},
        ],
        'schema': [seo.faq_schema(faqs)],
    })
