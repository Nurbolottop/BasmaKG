from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, format_html_join

from apps.contacts.models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'status_badge', 'type', 'name', 'phone_link', 'subject_short', 'has_file']
    list_display_links = ['id', 'name']
    list_filter = ['status', 'type', 'created_at']
    search_fields = ['name', 'phone', 'message', 'subject']
    list_editable = []
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'source_url', 'details_table', 'type', 'product', 'service', 'file_link']
    actions = ['mark_work', 'mark_done']
    fieldsets = [
        (None, {'fields': ['status', 'manager_note']}),
        ('Клиент', {'fields': ['name', 'phone', 'message']}),
        ('Заказ', {'fields': ['type', 'subject', 'service', 'product', 'details_table', 'file_link']}),
        ('Служебное', {'fields': ['created_at', 'source_url'], 'classes': ['collapse']}),
    ]

    COLORS = {'new': '#e8a400', 'work': '#2563eb', 'done': '#16a34a', 'cancel': '#9ca3af'}

    @admin.display(description='Статус', ordering='status')
    def status_badge(self, obj):
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:99px;font-size:11px;'
            'font-weight:600">{}</span>', self.COLORS.get(obj.status, '#999'), obj.get_status_display())

    @admin.display(description='Телефон', ordering='phone')
    def phone_link(self, obj):
        return format_html('<a href="tel:{}">{}</a>', obj.phone, obj.phone)

    @admin.display(description='Интересует')
    def subject_short(self, obj):
        text = obj.subject or (obj.product and obj.product.name) or (obj.service and obj.service.name) or ''
        return text[:50]

    @admin.display(description='Макет / файл')
    def file_link(self, obj):
        if not obj.file:
            return '—'
        return format_html('<a href="{}">Скачать файл</a>', reverse('lead_file', args=[obj.pk]))

    @admin.display(description='Файл', boolean=True)
    def has_file(self, obj):
        return bool(obj.file)

    @admin.display(description='Параметры')
    def details_table(self, obj):
        if not obj.details:
            return '—'
        return format_html('<table>{}</table>', format_html_join(
            '', '<tr><td style="padding:2px 12px 2px 0;color:#666">{}</td><td><b>{}</b></td></tr>',
            obj.details.items()))

    @admin.action(description='Взять в работу')
    def mark_work(self, request, queryset):
        queryset.update(status=Lead.STATUS_WORK)

    @admin.action(description='Отметить выполненными')
    def mark_done(self, request, queryset):
        queryset.update(status=Lead.STATUS_DONE)
