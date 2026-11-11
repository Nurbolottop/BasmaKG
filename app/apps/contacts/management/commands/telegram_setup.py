"""
Настройка Telegram-уведомлений.

    python manage.py telegram_setup            # показать группы, где состоит бот (из getUpdates)
    python manage.py telegram_setup --topics   # создать темы в TELEGRAM_CHAT_ID и отправить тест в каждую
"""
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.contacts import telegram


class Command(BaseCommand):
    help = 'Поиск ID группы и создание тем для заявок'

    def add_arguments(self, parser):
        parser.add_argument('--topics', action='store_true', help='Создать темы и отправить тестовые сообщения')

    def handle(self, *args, **opts):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise CommandError('TELEGRAM_BOT_TOKEN не задан в .env')
        me = telegram.api('getMe')
        self.stdout.write(f'Бот: @{me["username"]}')

        if not opts['topics']:
            seen = {}
            for u in telegram.api('getUpdates', allowed_updates='["message","my_chat_member"]'):
                for k in ('message', 'my_chat_member'):
                    chat = (u.get(k) or {}).get('chat')
                    if chat and chat.get('type') in ('group', 'supergroup'):
                        seen[chat['id']] = chat
            if not seen:
                self.stdout.write('Групп не найдено. Напишите в группе /start@' + me['username'] + ' и повторите.')
            for cid, chat in seen.items():
                info = telegram.api('getChat', chat_id=cid)
                member = telegram.api('getChatMember', chat_id=cid, user_id=me['id'])
                self.stdout.write(f'{cid}  «{chat.get("title")}»  темы: {"да" if info.get("is_forum") else "нет"}  '
                                  f'бот: {member.get("status")}, управление темами: {member.get("can_manage_topics")}')
            return

        if not settings.TELEGRAM_CHAT_ID:
            raise CommandError('TELEGRAM_CHAT_ID не задан в .env')
        for key, (name, _) in telegram.TOPICS.items():
            thread = telegram.get_thread_id(key)
            telegram.send_to_topic(key, f'✅ <b>{name}</b>\nСюда будут приходить заявки этого типа с сайта basma.kg.')
            self.stdout.write(self.style.SUCCESS(f'{name}: тема {thread or "— (общий чат)"}'))
