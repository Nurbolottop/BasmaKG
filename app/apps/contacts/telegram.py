"""Уведомления о заявках в Telegram-группу, по темам (forum topics).

Каждый тип заявки уходит в свою тему. Темы создаются автоматически при первой
заявке (боту нужны права администратора «Управление темами»). Если в группе темы
выключены — сообщения уходят в общий чат.
"""
import html
import logging
import threading

import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)
API = 'https://api.telegram.org/bot{token}/{method}'

# тип заявки -> (название темы, цвет иконки из палитры Telegram)
TOPICS = {
    'callback': ('📞 Звонки и вопросы', 0x6FB9F0),
    'order': ('🛒 Заказы товаров', 0xFFD67E),
    'stamp': ('🔖 Конструктор печати', 0xCB86DB),
    'service': ('🧾 Заявки на услуги', 0x8EEE98),
}


class TelegramError(Exception):
    pass


def api(method, files=None, timeout=15, **params):
    url = API.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)
    resp = requests.post(url, data=params, files=files, timeout=timeout)
    data = resp.json()
    if not data.get('ok'):
        raise TelegramError(data.get('description', resp.text))
    return data['result']


def get_thread_id(lead_type, chat_id=None, force_new=False):
    """ID темы для типа заявки; создаёт тему при необходимости. None — группа без тем."""
    from apps.contacts.models import TelegramTopic

    chat_id = str(chat_id or settings.TELEGRAM_CHAT_ID)
    name, color = TOPICS.get(lead_type, TOPICS['callback'])
    topic = TelegramTopic.objects.filter(key=lead_type, chat_id=chat_id).first()
    if topic and not force_new:
        return topic.thread_id
    try:
        result = api('createForumTopic', chat_id=chat_id, name=name, icon_color=color)
    except TelegramError as e:
        logger.warning('Telegram: не удалось создать тему %s: %s', name, e)
        return None  # группа не форум или нет прав — шлём в общий чат
    TelegramTopic.objects.update_or_create(
        key=lead_type, defaults={'chat_id': chat_id, 'thread_id': result['message_thread_id'], 'name': name})
    return result['message_thread_id']


def format_lead(lead):
    e = html.escape
    lines = [
        f'🟡 <b>Заявка #{lead.pk}</b> — {e(lead.get_type_display())}',
        '',
        f'👤 {e(lead.name)}',
        f'📞 {e(lead.phone)}',  # Telegram сам делает номер кликабельным (tel: в HTML не поддерживается)
    ]
    if lead.subject:
        lines.append(f'📌 {e(lead.subject)}')
    if lead.service:
        lines.append(f'🧾 Услуга: {e(lead.service.name_ru or lead.service.name)}')
    if lead.product:
        lines.append(f'🔖 Товар: {e(lead.product.name_ru or lead.product.name)}')
    for key, value in (lead.details or {}).items():
        lines.append(f'• {e(key)}: {e(str(value))}')
    if lead.message:
        lines += ['', f'💬 {e(lead.message)}']
    if lead.source_url:
        lang = 'KG' if '/ky/' in lead.source_url else 'RU'
        lines += ['', f'🌐 Страница ({lang}): {e(lead.source_url)}']
    admin_url = settings.SITE_URL.rstrip('/') + reverse('admin:contacts_lead_change', args=[lead.pk])
    lines += [f'<a href="{admin_url}">Открыть в админке</a>']
    return '\n'.join(lines)


def send_to_topic(lead_type, text, document=None, caption=''):
    """Отправка в тему; если тему удалили в Telegram — пересоздаём и повторяем один раз."""
    chat_id = settings.TELEGRAM_CHAT_ID
    for attempt in (1, 2):
        thread_id = get_thread_id(lead_type, force_new=(attempt == 2))
        extra = {'message_thread_id': thread_id} if thread_id else {}
        try:
            api('sendMessage', chat_id=chat_id, text=text, parse_mode='HTML',
                disable_web_page_preview=True, **extra)
            if document:
                name, fh = document
                api('sendDocument', chat_id=chat_id, caption=caption, files={'document': (name, fh)},
                    timeout=60, **extra)
            return
        except TelegramError as e:
            if attempt == 1 and thread_id and 'thread' in str(e).lower():
                continue  # тема удалена — создаём заново
            raise


def _send(lead_id):
    from apps.contacts.models import Lead

    try:
        lead = Lead.objects.select_related('product', 'service').get(pk=lead_id)
    except Lead.DoesNotExist:
        return
    try:
        document = None
        if lead.file:
            fh = lead.file.open('rb')
            document = (f'lead-{lead.pk}' + lead.file.name[lead.file.name.rfind('.'):], fh)
        send_to_topic(lead.type, format_lead(lead), document=document, caption=f'Макет к заявке #{lead.pk}')
    except Exception:  # уведомление не должно ронять приём заявки
        logger.exception('Telegram notify failed for lead %s', lead_id)
    finally:
        if lead.file:
            lead.file.close()


def notify_new_lead(lead):
    if not (settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID):
        return
    threading.Thread(target=_send, args=(lead.pk,), daemon=True).start()
