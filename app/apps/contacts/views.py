import mimetypes
import os

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from django.urls import reverse

from apps.base import seo
from apps.cms.models import FAQ
from apps.contacts.forms import LeadForm
from apps.contacts.models import Lead
from apps.contacts.telegram import notify_new_lead

RATE_LIMIT = 6          # заявок
RATE_WINDOW = 60 * 10   # за 10 минут с одного IP


def _client_ip(request):
    # X-Real-IP выставляет наш nginx ($remote_addr) и перезаписывает значение клиента.
    # X-Forwarded-For не используем: первый адрес в нём может подставить кто угодно.
    return request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR', '')


def _wants_json(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'


@require_POST
def lead_create(request):
    key = f'lead-rate:{_client_ip(request)}'
    if cache.get(key, 0) >= RATE_LIMIT:
        msg = _('Слишком много заявок. Пожалуйста, позвоните нам.')
        if _wants_json(request):
            return JsonResponse({'ok': False, 'errors': {'__all__': [msg]}}, status=429)
        messages.error(request, msg)
        return redirect(request.META.get('HTTP_REFERER') or '/')

    form = LeadForm(request.POST, request.FILES)
    if form.is_valid():
        lead = form.save(commit=False)
        lead.details = form.collect_details(request.POST)
        lead.source_url = (request.META.get('HTTP_REFERER') or '')[:500]
        lead.save()
        cache.set(key, cache.get(key, 0) + 1, RATE_WINDOW)
        notify_new_lead(lead)
        if _wants_json(request):
            return JsonResponse({'ok': True, 'id': lead.pk})
        return redirect('contacts:thanks')

    # Бот, заполнивший honeypot, получает «успех» и ничего не сохраняется
    if form.cleaned_data.get('website'):
        return JsonResponse({'ok': True}) if _wants_json(request) else redirect('contacts:thanks')

    errors = {field: [str(e) for e in errs] for field, errs in form.errors.items()}
    if _wants_json(request):
        return JsonResponse({'ok': False, 'errors': errors}, status=400)
    for errs in errors.values():
        for err in errs:
            messages.error(request, err)
    return redirect(request.META.get('HTTP_REFERER') or '/')


def contacts(request):
    faqs = FAQ.objects.filter(is_active=True)[:6]
    return render(request, 'contacts/contacts.html', {
        'faqs': faqs,
        'breadcrumbs': [{'name': _('Главная'), 'url': reverse('base:home')},
                        {'name': _('Контакты'), 'url': reverse('contacts:contacts')}],
        'schema': [{'@context': 'https://schema.org', '@type': 'ContactPage',
                    'url': seo.absolute(reverse('contacts:contacts')), 'about': {'@id': seo.org_id()}},
                   seo.faq_schema(faqs)],
    })


def thanks(request):
    return render(request, 'contacts/thanks.html', {'noindex': True})


@staff_member_required
def lead_file(request, pk):
    """Макеты клиентов отдаём только сотрудникам. Прямой доступ к /media/leads/ закрыт в nginx."""
    lead = get_object_or_404(Lead, pk=pk)
    if not lead.file:
        raise Http404
    try:
        fh = lead.file.open('rb')
    except FileNotFoundError:
        raise Http404
    name = f'lead-{lead.pk}{os.path.splitext(lead.file.name)[1]}'
    response = FileResponse(fh, as_attachment=True, filename=name,
                            content_type=mimetypes.guess_type(name)[0] or 'application/octet-stream')
    response['X-Content-Type-Options'] = 'nosniff'
    return response
