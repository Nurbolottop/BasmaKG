from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from django_resized import ResizedImageField

from apps.base.utils import unique_slug

ICON_CHOICES = [
    ('stamp', 'Печать'),
    ('briefcase', 'Портфель / бизнес'),
    ('calculator', 'Калькулятор'),
    ('certificate', 'Сертификат / лицензия'),
    ('bolt', 'Молния / скорость'),
    ('shield', 'Щит / гарантия'),
    ('clock', 'Часы'),
    ('pen', 'Ручка / макет'),
    ('truck', 'Доставка'),
    ('wallet', 'Кошелёк / цена'),
    ('star', 'Звезда'),
    ('chat', 'Чат'),
]


class Service(models.Model):
    name = models.CharField('Название', max_length=150)
    slug = models.SlugField('URL', max_length=170, unique=True, blank=True)
    icon = models.CharField('Иконка', max_length=20, choices=ICON_CHOICES, default='briefcase')
    short_description = models.CharField('Кратко (для карточки)', max_length=255)
    description = RichTextUploadingField('Подробное описание', blank=True)
    features = models.TextField('Что входит', blank=True, help_text='Каждый пункт с новой строки')
    price_text = models.CharField('Цена', max_length=80, blank=True, help_text='Например: от 1 500 сом')
    term_text = models.CharField('Срок', max_length=80, blank=True, help_text='Например: 1 день')
    image = ResizedImageField('Изображение', size=[900, 900], quality=88, force_format='WEBP',
                              upload_to='services/', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)
    meta_title = models.CharField('SEO title', max_length=200, blank=True, help_text='До 60 символов')
    meta_description = models.TextField('SEO description', blank=True, help_text='120–160 символов')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('cms:service', args=[self.slug])

    @property
    def sitemap_image(self):
        return self.image.url if self.image else None

    @property
    def features_list(self):
        return [line.strip(' -•') for line in self.features.splitlines() if line.strip()]


class Advantage(models.Model):
    title = models.CharField('Заголовок', max_length=120)
    text = models.CharField('Текст', max_length=255)
    icon = models.CharField('Иконка', max_length=20, choices=ICON_CHOICES, default='star')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Преимущество'
        verbose_name_plural = 'Преимущества'

    def __str__(self):
        return self.title


class Step(models.Model):
    title = models.CharField('Заголовок', max_length=120)
    text = models.CharField('Текст', max_length=255)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Шаг «Как мы работаем»'
        verbose_name_plural = 'Шаги «Как мы работаем»'

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField('Вопрос', max_length=255)
    answer = models.TextField('Ответ')
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Вопрос-ответ'
        verbose_name_plural = 'Вопросы и ответы'

    def __str__(self):
        return self.question


class Review(models.Model):
    name = models.CharField('Имя', max_length=100)
    company = models.CharField('Компания / должность', max_length=150, blank=True)
    text = models.TextField('Отзыв')
    rating = models.PositiveSmallIntegerField('Оценка', default=5,
                                              choices=[(i, i) for i in range(1, 6)])
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        ordering = ['order', '-id']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f'{self.name}: {self.text[:40]}'


class Page(models.Model):
    """Текстовые страницы: «О компании», «Политика конфиденциальности» и т.п."""
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', max_length=120, unique=True,
                            help_text='Для страницы «О компании» — about')
    lead = models.TextField('Подзаголовок', blank=True)
    content = RichTextUploadingField('Содержимое', blank=True)
    is_active = models.BooleanField('Опубликована', default=True)
    updated_at = models.DateTimeField('Изменено', auto_now=True)
    meta_title = models.CharField('SEO title', max_length=200, blank=True, help_text='До 60 символов')
    meta_description = models.TextField('SEO description', blank=True, help_text='120–160 символов')

    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.slug == 'about':
            return reverse('cms:about')
        return reverse('cms:page', args=[self.slug])
