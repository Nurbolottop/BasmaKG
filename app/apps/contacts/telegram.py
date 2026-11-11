import html
import logging
import threading

import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)
API = 'https://api.telegram.org/bot{token}/{method}'


def _send(lead_id):
    from apps.contacts.models import Lead

    token, chat_id = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    try:
        lead = Lead.objects.select_related('product', 'service').get(pk=lead_id)
    except Lead.DoesNotExist:
        return

    e = html.escape
    lines = [
        f'🟡 <b>Новая заявка #{lead.pk}</b> — {e(lead.get_type_display())}',
        '',
        f'👤 {e(lead.name)}',
        f'📞 {e(lead.phone)}',
    ]
    if lead.subject:
        lines.append(f'📌 {e(lead.subject)}')
    if lead.service:
        lines.append(f'🧾 Услуга: {e(lead.service.name)}')
    if lead.product:
        lines.append(f'🔖 Товар: {e(lead.product.name)}')
    for key, value in (lead.details or {}).items():
        lines.append(f'• {e(key)}: {e(str(value))}')
    if lead.message:
        lines += ['', f'💬 {e(lead.message)}']
    admin_url = settings.SITE_URL.rstrip('/') + reverse('admin:contacts_lead_change', args=[lead.pk])
    lines += ['', f'<a href="{admin_url}">Открыть в админке</a>']

    try:
        requests.post(API.format(token=token, method='sendMessage'), timeout=10, data={
            'chat_id': chat_id, 'text': '\n'.join(lines), 'parse_mode': 'HTML',
            'disable_web_page_preview': True,
        }).raise_for_status()
        if lead.file:
            with lead.file.open('rb') as fh:
                requests.post(API.format(token=token, method='sendDocument'), timeout=30,
                              data={'chat_id': chat_id, 'caption': f'Макет к заявке #{lead.pk}'},
                              files={'document': (lead.file.name.rsplit('/', 1)[-1], fh)})
    except Exception:  # уведомление не должно ронять приём заявки
        logger.exception('Telegram notify failed for lead %s', lead_id)


def notify_new_lead(lead):
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    threading.Thread(target=_send, args=(lead.pk,), daemon=True).start()
