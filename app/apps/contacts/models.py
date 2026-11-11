import os
import uuid

from django.db import models


def lead_upload_to(instance, filename):
    """Случайное имя файла: макеты клиентов нельзя найти перебором URL."""
    ext = os.path.splitext(filename)[1].lower()[:10]
    return f'leads/{uuid.uuid4().hex}{ext}'


class Lead(models.Model):
    TYPE_CALLBACK = 'callback'
    TYPE_ORDER = 'order'
    TYPE_STAMP = 'stamp'
    TYPE_SERVICE = 'service'
    TYPE_CHOICES = [
        (TYPE_CALLBACK, 'Обратный звонок'),
        (TYPE_ORDER, 'Заказ товара'),
        (TYPE_STAMP, 'Конструктор печати'),
        (TYPE_SERVICE, 'Заявка на услугу'),
    ]

    STATUS_NEW = 'new'
    STATUS_WORK = 'work'
    STATUS_DONE = 'done'
    STATUS_CANCEL = 'cancel'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_WORK, 'В работе'),
        (STATUS_DONE, 'Выполнена'),
        (STATUS_CANCEL, 'Отменена'),
    ]

    type = models.CharField('Тип', max_length=20, choices=TYPE_CHOICES, default=TYPE_CALLBACK)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    name = models.CharField('Имя', max_length=120)
    phone = models.CharField('Телефон', max_length=40)
    message = models.TextField('Комментарий', blank=True)
    subject = models.CharField('Что интересует', max_length=255, blank=True)
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='Товар / оснастка')
    service = models.ForeignKey('cms.Service', on_delete=models.SET_NULL, null=True, blank=True,
                                verbose_name='Услуга')
    details = models.JSONField('Параметры заказа', default=dict, blank=True)
    file = models.FileField('Макет / файл', upload_to=lead_upload_to, blank=True)
    source_url = models.CharField('Страница', max_length=500, blank=True)
    manager_note = models.TextField('Заметка менеджера', blank=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return f'#{self.pk} {self.name} {self.phone}'


class TelegramTopic(models.Model):
    """Тема (forum topic) в группе менеджеров для каждого типа заявок."""
    key = models.CharField('Тип заявок', max_length=20, unique=True, choices=Lead.TYPE_CHOICES)
    chat_id = models.CharField('ID группы', max_length=40)
    thread_id = models.BigIntegerField('ID темы')
    name = models.CharField('Название темы', max_length=128)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Тема в Telegram'
        verbose_name_plural = 'Темы в Telegram'

    def __str__(self):
        return self.name
