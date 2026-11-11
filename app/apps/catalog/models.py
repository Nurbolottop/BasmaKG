from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_resized import ResizedImageField

from apps.base.utils import unique_slug


class Category(models.Model):
    name = models.CharField('Название', max_length=120)
    slug = models.SlugField('URL', max_length=140, unique=True, blank=True,
                            help_text='Заполнится автоматически')
    tagline = models.CharField('Короткий слоган', max_length=160, blank=True)
    description = RichTextUploadingField('Описание', blank=True)
    image = ResizedImageField('Изображение', size=[900, 900], quality=88, force_format='WEBP',
                              upload_to='catalog/categories/', blank=True)
    seo_text = RichTextUploadingField('SEO-текст внизу страницы', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)
    updated_at = models.DateTimeField('Изменена', auto_now=True)
    meta_title = models.CharField('SEO title', max_length=200, blank=True, help_text='До 60 символов')
    meta_description = models.TextField('SEO description', blank=True, help_text='120–160 символов')

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:category', args=[self.slug])

    @property
    def sitemap_image(self):
        return self.image.url if self.image else None


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True, category__is_active=True)


class Product(models.Model):
    SHAPE_ROUND = 'round'
    SHAPE_SQUARE = 'square'
    SHAPE_RECT = 'rect'
    SHAPE_CHOICES = [
        (SHAPE_ROUND, _('Круглая')),
        (SHAPE_SQUARE, _('Квадратная')),
        (SHAPE_RECT, _('Прямоугольная')),
    ]

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products',
                                 verbose_name='Категория')
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', max_length=220, unique=True, blank=True)
    brand = models.CharField('Бренд', max_length=80, blank=True, help_text='Trodat, Colop, Ideal…')
    size = models.CharField('Размер оттиска', max_length=80, blank=True, help_text='Например: Ø 40 мм')
    shape = models.CharField('Форма оттиска', max_length=10, choices=SHAPE_CHOICES, blank=True)
    short_description = models.CharField('Кратко', max_length=255, blank=True)
    description = RichTextUploadingField('Описание', blank=True)
    price = models.DecimalField('Цена, сом', max_digits=10, decimal_places=0, null=True, blank=True,
                                help_text='Пусто — «цена по запросу»')
    price_from = models.BooleanField('Цена «от»', default=False)
    old_price = models.DecimalField('Старая цена', max_digits=10, decimal_places=0, null=True, blank=True)
    image = ResizedImageField('Главное фото', size=[1000, 1000], quality=88, force_format='WEBP',
                              upload_to='catalog/products/', blank=True)
    in_stock = models.BooleanField('В наличии', default=True)
    is_popular = models.BooleanField('Хит', default=False)
    in_constructor = models.BooleanField(
        'Доступна в конструкторе печати', default=False,
        help_text='Оснастка появится в списке выбора на странице «Заказать печать онлайн»',
    )
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Изменён', auto_now=True)
    meta_title = models.CharField('SEO title', max_length=200, blank=True, help_text='До 60 символов')
    meta_description = models.TextField('SEO description', blank=True, help_text='120–160 символов')

    objects = ProductQuerySet.as_manager()

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('catalog:product', args=[self.slug])

    @property
    def cover(self):
        return self.image or self.category.image

    @property
    def sitemap_image(self):
        return self.cover.url if self.cover else None


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = ResizedImageField('Фото', size=[1000, 1000], quality=88, force_format='WEBP',
                              upload_to='catalog/products/gallery/')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Фото'
        verbose_name_plural = 'Галерея'

    def __str__(self):
        return f'Фото {self.product}'
