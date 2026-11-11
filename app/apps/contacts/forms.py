import os
import re

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from apps.contacts.models import Lead

ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.webp', '.heic', '.doc', '.docx', '.cdr', '.ai'}

# Параметры конструктора печати, которые сохраняем в Lead.details
DETAIL_FIELDS = {
    'd_kind': 'Что изготовить',
    'd_shape': 'Форма',
    'd_org': 'Название организации',
    'd_inn': 'ИНН',
    'd_center': 'Текст в центре',
    'd_city': 'Город',
    'd_ink': 'Цвет краски',
    'd_qty': 'Количество',
    'd_urgent': 'Срочно',
    'd_total': 'Ориентировочная сумма',
}


class LeadForm(forms.ModelForm):
    # honeypot: люди поле не видят, боты заполняют
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}))
    agree = forms.BooleanField(required=True, error_messages={'required': _('Нужно согласие на обработку данных')})

    class Meta:
        model = Lead
        fields = ['type', 'name', 'phone', 'message', 'subject', 'product', 'service', 'file']
        error_messages = {
            'name': {'required': _('Как к вам обращаться?')},
            'phone': {'required': _('Укажите телефон для связи')},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'].required = False

    def clean_type(self):
        return self.cleaned_data.get('type') or Lead.TYPE_CALLBACK

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        if len(re.sub(r'\D', '', phone)) < 9:
            raise forms.ValidationError(_('Проверьте номер телефона'))
        return phone

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if not f:
            return f
        ext = os.path.splitext(f.name)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError(_('Допустимые форматы: PDF, JPG, PNG, WEBP, HEIC, DOC, CDR, AI'))
        if f.size > settings.LEAD_FILE_MAX_SIZE:
            raise forms.ValidationError(_('Файл больше 10 МБ'))
        return f

    def clean(self):
        data = super().clean()
        if data.get('website'):
            raise forms.ValidationError('spam')
        return data

    def collect_details(self, post):
        details = {}
        for key, label in DETAIL_FIELDS.items():
            value = (post.get(key) or '').strip()[:300]
            if value:
                details[label] = value
        return details
