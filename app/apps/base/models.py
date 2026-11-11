from ckeditor_uploader.fields import RichTextUploadingField
from django.core.cache import cache
from django.db import models


class SingletonModel(models.Model):
    """Модель, у которой в базе всегда ровно одна запись (pk=1)."""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete(self.cache_key())

    def delete(self, *args, **kwargs):
        pass  # синглтон не удаляется

    @classmethod
    def cache_key(cls):
        return f'singleton:{cls._meta.label_lower}'

    @classmethod
    def load(cls):
        obj = cache.get(cls.cache_key())
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set(obj.cache_key(), obj, 60 * 10)
        return obj


class SiteSettings(SingletonModel):
    # Бренд
    site_name = models.CharField('Название', max_length=100, default='Basma Service')
    tagline = models.CharField(
        'Слоган', max_length=200,
        default='Печати, штампы и регистрация бизнеса в Манасе',
    )

    # Первый экран
    hero_title = models.CharField(
        'Заголовок первого экрана (H1)', max_length=200,
        default='Печать|за 1 час.|Бизнес —|под ключ.',
        help_text='Строки разделяйте символом |. 2-я строка — жёлтая плашка, 3-я — серая',
    )
    hero_text = models.TextField(
        'Текст первого экрана',
        default='Изготовим печать или штамп по вашему макету, зарегистрируем компанию '
                'и возьмём на себя бухгалтерию. Всё в одном месте — быстро и без ошибок.',
    )

    # Контакты
    phone = models.CharField('Телефон', max_length=50, default='0225 005 007')
    phone_2 = models.CharField('Доп. телефон', max_length=50, blank=True)
    whatsapp = models.CharField(
        'WhatsApp (номер в международном формате)', max_length=30, blank=True,
        help_text='Только цифры, например 996225005007',
    )
    telegram = models.CharField('Telegram (username без @)', max_length=64, blank=True)
    email = models.EmailField('Email', blank=True)
    city = models.CharField('Город', max_length=100, default='г. Манас')
    address = models.CharField('Адрес', max_length=255, blank=True)
    working_hours = models.CharField('Режим работы', max_length=200, default='Пн–Сб: 9:00 – 18:00')
    map_embed_url = models.URLField(
        'Ссылка для встраивания карты', max_length=1000, blank=True,
        help_text='2ГИС / Google Maps → «Поделиться» → «Встроить» → src из iframe',
    )
    map_link = models.URLField('Ссылка на карту (2ГИС/Google)', max_length=500, blank=True)

    # Соцсети
    instagram = models.URLField('Instagram', blank=True, default='https://www.instagram.com/basma_service/')
    youtube = models.URLField('YouTube', blank=True)
    tiktok = models.URLField('TikTok', blank=True)
    facebook = models.URLField('Facebook', blank=True)

    # Цифры
    stat_years = models.CharField('Цифра: лет опыта', max_length=20, default='10+')
    stat_clients = models.CharField('Цифра: клиентов', max_length=20, default='5 000+')
    stat_speed = models.CharField('Цифра: срок изготовления', max_length=20, default='1 час')

    # Для разметки schema.org (карточка организации в Google / Яндекс)
    latitude = models.DecimalField('Широта', max_digits=9, decimal_places=6, null=True, blank=True,
                                   help_text='Например 42.524600 — из 2ГИС/Google Maps')
    longitude = models.DecimalField('Долгота', max_digits=9, decimal_places=6, null=True, blank=True)
    opening_hours_schema = models.CharField(
        'Часы работы для поисковиков', max_length=100, default='Mo-Sa 09:00-18:00',
        help_text='Формат schema.org: Mo-Fr 09:00-18:00, Sa 10:00-15:00')
    price_range = models.CharField('Диапазон цен', max_length=50, default='от 250 сом', blank=True)

    # SEO
    meta_title = models.CharField('SEO title главной', max_length=200, blank=True,
                                  help_text='До 60 символов. Пусто — заголовок по умолчанию')
    meta_description = models.TextField('SEO description главной', blank=True,
                                        help_text='120–160 символов')
    seo_text = RichTextUploadingField('SEO-текст внизу главной', blank=True)
    og_image = models.ImageField('Картинка для соцсетей (OG)', upload_to='seo/', blank=True,
                                 help_text='1200×630. Пусто — фирменная картинка по умолчанию')
    google_verification = models.CharField('Google Search Console: код', max_length=100, blank=True,
                                           help_text='Только content из meta google-site-verification')
    yandex_verification = models.CharField('Яндекс.Вебмастер: код', max_length=100, blank=True)
    ga4_id = models.CharField('Google Analytics 4 ID', max_length=30, blank=True, help_text='G-XXXXXXX')
    ym_id = models.CharField('Яндекс.Метрика ID', max_length=20, blank=True, help_text='Только цифры')
    head_scripts = models.TextField(
        'Доп. код в <head>', blank=True,
        help_text='Прочие счётчики и пиксели (Meta Pixel и т.п.)',
    )

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return 'Настройки сайта'

    @property
    def hero_lines(self):
        styles = ['', 'mark', 'muted', '']
        return [{'text': t.strip(), 'style': styles[i] if i < len(styles) else ''}
                for i, t in enumerate(self.hero_title.split('|')) if t.strip()]

    @property
    def phone_href(self):
        digits = ''.join(c for c in self.phone if c.isdigit() or c == '+')
        if digits.startswith('0'):
            digits = '+996' + digits[1:]
        return digits

    @property
    def whatsapp_url(self):
        return f'https://wa.me/{self.whatsapp}' if self.whatsapp else ''

    @property
    def telegram_url(self):
        return f'https://t.me/{self.telegram.lstrip("@")}' if self.telegram else ''


class SeoMeta(models.Model):
    """Ручная настройка SEO для любой страницы по её адресу."""
    path = models.CharField(
        'Адрес страницы', max_length=255, unique=True,
        help_text='Без домена и языка, например: /catalog/ или /services/registratsiya-firmy/')
    title = models.CharField('Title', max_length=200, blank=True, help_text='До 60 символов')
    description = models.TextField('Description', blank=True, help_text='120–160 символов')
    og_image = models.ImageField('Картинка для соцсетей', upload_to='seo/', blank=True)
    noindex = models.BooleanField('Скрыть от поисковиков (noindex)', default=False)

    class Meta:
        verbose_name = 'SEO страницы'
        verbose_name_plural = 'SEO страниц'
        ordering = ['path']

    def __str__(self):
        return self.path

    def save(self, *args, **kwargs):
        self.path = '/' + self.path.strip().strip('/') + '/' if self.path.strip('/') else '/'
        super().save(*args, **kwargs)
        cache.delete(self.cache_key(self.path))

    def delete(self, *args, **kwargs):
        cache.delete(self.cache_key(self.path))
        return super().delete(*args, **kwargs)

    @staticmethod
    def cache_key(path):
        return f'seometa:{path}'

    @classmethod
    def for_path(cls, path):
        key = cls.cache_key(path)
        obj = cache.get(key)
        if obj is None:
            obj = cls.objects.filter(path=path).first() or False
            cache.set(key, obj, 60 * 10)
        return obj or None
