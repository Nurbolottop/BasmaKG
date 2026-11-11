from django.utils.text import slugify

_TRANSLIT = {
    'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh',
    'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
    'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
    'ч': 'ch', 'ш': 'sh', 'щ': 'sch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu',
    'я': 'ya',
    # кыргызские буквы
    'ң': 'ng', 'ө': 'o', 'ү': 'u',
}


def translit_slug(value, max_length=200):
    """Латинский slug из кириллицы: «Ручные оснастки» → «ruchnye-osnastki»."""
    value = ''.join(_TRANSLIT.get(ch, ch) for ch in str(value).lower())
    return slugify(value)[:max_length].strip('-')


def unique_slug(instance, value, field='slug'):
    base = translit_slug(value) or 'item'
    slug, n = base, 2
    model = type(instance)
    while model.objects.filter(**{field: slug}).exclude(pk=instance.pk).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug
