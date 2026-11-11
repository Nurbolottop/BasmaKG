"""
Стартовое наполнение сайта Basma Service.

    python manage.py seed_basma            # создаёт только то, чего ещё нет
    python manage.py seed_basma --reset    # удаляет каталог/контент и создаёт заново

Цены товаров — ОРИЕНТИРОВОЧНЫЕ, их нужно сверить с прайсом и поправить в админке.
"""
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.base.models import SiteSettings
from apps.catalog.models import Category, Product
from apps.cms.models import FAQ, Advantage, Page, Service, Step

from . import _seed_i18n as I18N

MEDIA = Path(__file__).resolve().parents[2] / 'seed_media'

CATEGORIES = [
    ('Автоматические оснастки', 'avtomaticheskie-osnastki', 'Быстро, удобно и надёжно', 'cat-automatic.png',
     'Самонаборные и автоматические оснастки Trodat, Colop, Ideal. Встроенная штемпельная подушка, '
     'чёткий оттиск без смазывания — тысячи оттисков без дозаправки.'),
    ('Ручные оснастки', 'ruchnye-osnastki', 'Доступно и практично', 'cat-manual.png',
     'Классические ручные оснастки из пластика и дерева. Бюджетный вариант для нечастого использования.'),
    ('Карманные оснастки', 'karmannye-osnastki', 'Компактно, удобно в дороге', 'cat-pocket.png',
     'Печать всегда с собой: карманные оснастки с защитной крышкой помещаются в карман или сумку.'),
    ('Флеш-печати', 'flesh-pechati', 'Максимальная чёткость и долговечность', 'cat-flash.png',
     'Флеш-печати с пропитанной краской: идеально тонкие линии, защитные элементы и до 50 000 оттисков.'),
    ('Расходные материалы', 'rashodnye-materialy', 'Всё необходимое в наличии', 'cat-supplies.png',
     'Штемпельная краска, сменные подушки, клише, полимер — всё для обслуживания ваших печатей.'),
]

# (категория-slug, название, бренд, размер, форма, цена, «от», хит, в конструкторе, кратко)
PRODUCTS = [
    ('avtomaticheskie-osnastki', 'Trodat Printy 4642', 'Trodat', 'Ø 42 мм', 'round', 1200, False, True, True,
     'Самая популярная автоматическая оснастка для круглой печати организации'),
    ('avtomaticheskie-osnastki', 'Colop Printer R40', 'Colop', 'Ø 40 мм', 'round', 1100, False, True, True,
     'Надёжная австрийская оснастка с крышкой, подушка меняется за секунды'),
    ('avtomaticheskie-osnastki', 'Ideal 46042', 'Ideal', 'Ø 42 мм', 'round', 900, False, False, True,
     'Доступная автоматическая оснастка — оптимальное соотношение цены и качества'),
    ('avtomaticheskie-osnastki', 'Trodat Printy 4924', 'Trodat', '40 × 40 мм', 'square', 1300, False, False, True,
     'Квадратный оттиск — для штампов «Оплачено», «Принято» и логотипов'),
    ('avtomaticheskie-osnastki', 'Trodat Printy 4912', 'Trodat', '47 × 18 мм', 'rect', 950, False, True, True,
     'Прямоугольный штамп с реквизитами, адресом или ФИО'),
    ('ruchnye-osnastki', 'Ручная оснастка пластиковая', '', 'Ø 40 мм', 'round', 500, False, False, True,
     'Бюджетная ручная оснастка с удобной ручкой'),
    ('ruchnye-osnastki', 'Ручная оснастка «Классика» с футляром', '', 'Ø 40 мм', 'round', 700, False, False, True,
     'Классическая оснастка с защитным футляром для клише'),
    ('karmannye-osnastki', 'Trodat Mobile Printy 9342', 'Trodat', 'Ø 40 мм', 'round', 1400, False, True, True,
     'Карманная автоматическая оснастка с защитной крышкой'),
    ('karmannye-osnastki', 'Colop Pocket Stamp R40', 'Colop', 'Ø 40 мм', 'round', 1350, False, False, True,
     'Компактная печать для курьеров, ИП и выездных менеджеров'),
    ('flesh-pechati', 'Флеш-печать круглая', '', 'Ø 40 мм', 'round', 1800, True, False, True,
     'Пропитанная краской флеш-печать с высокой детализацией'),
    ('flesh-pechati', 'Факсимиле (флеш)', '', '38 × 14 мм', 'rect', 1500, True, False, False,
     'Точная копия подписи — подписывайте документы быстрее'),
    ('rashodnye-materialy', 'Штемпельная краска 25 мл', 'Trodat', '', '', 250, False, False, False,
     'Синяя, фиолетовая, красная, чёрная, зелёная'),
    ('rashodnye-materialy', 'Сменная штемпельная подушка', 'Trodat / Colop', '', '', 300, True, False, False,
     'Подходит для автоматических оснасток Trodat и Colop'),
]

SERVICES = [
    ('Изготовление печатей и штампов', 'izgotovlenie-pechatey', 'stamp', 'service-stamps.png',
     'Печати ООО, ИП, врача, факсимиле и штампы любой сложности — по вашему макету или с нуля.',
     'Разработка макета бесплатно\nПечати организаций и ИП\nПечати врача и факсимиле\nШтампы с реквизитами\n'
     'Флеш-печати с защитой\nВосстановление печати по оттиску',
     'от 500 сом', 'от 1 часа'),
    ('Регистрация фирмы', 'registratsiya-firmy', 'briefcase', 'service-registration.png',
     'Зарегистрируем ИП, ОсОО или общественное объединение и подготовим все документы.',
     'Консультация и выбор формы бизнеса\nПодготовка устава и решений\nПодача документов в Минюст\n'
     'Постановка на учёт в ГНС и Соцфонде\nИзготовление печати в подарок',
     'по запросу', 'от 3 дней'),
    ('Бухгалтерские услуги', 'buhgalterskie-uslugi', 'calculator', 'service-accounting.png',
     'Ведём учёт и сдаём отчётность в ГНС и Соцфонд вовремя и без ошибок. ЭСФ, ИП и ОсОО.',
     'Отчётность в ГНС и Соцфонд\nЭлектронные счета-фактуры (ЭСФ)\nНулевая отчётность\nЗарплата и кадры\n'
     'Восстановление учёта',
     'от 2 000 сом/мес', 'ежемесячно'),
    ('Получение лицензий', 'poluchenie-litsenziy', 'certificate', 'service-license.png',
     'Поможем получить лицензию или разрешение: соберём пакет документов и сопроводим до результата.',
     'Анализ требований к деятельности\nПодготовка пакета документов\nПодача и сопровождение\n'
     'Консультации на каждом этапе',
     'по запросу', 'зависит от вида'),
]

ADVANTAGES = [
    ('Печать за 1 час', 'Срочное изготовление при вас — пока пьёте кофе.', 'bolt'),
    ('Макет бесплатно', 'Разработаем и согласуем оттиск без доплаты.', 'pen'),
    ('Оригинальные оснастки', 'Trodat, Colop, Ideal — гарантия от производителя.', 'shield'),
    ('Всё в одном месте', 'Регистрация, печать, бухгалтерия и лицензии — одно окно.', 'briefcase'),
]

STEPS = [
    ('Заявка', 'Оставьте заявку на сайте, в WhatsApp или позвоните — ответим за 5 минут.'),
    ('Макет', 'Отрисуем оттиск и пришлём на согласование. Правки — бесплатно.'),
    ('Изготовление', 'Изготавливаем на лазерном оборудовании от 1 часа.'),
    ('Готово', 'Забираете в офисе или получаете доставкой по городу.'),
]

FAQS = [
    ('Какие документы нужны для изготовления печати организации?',
     'Для печати ОсОО — копия свидетельства о регистрации и паспорт руководителя (или доверенность). '
     'Для ИП — свидетельство/патент и паспорт. Можно прислать фото документов в WhatsApp.'),
    ('Сколько времени занимает изготовление?',
     'Стандартно — от 1 часа после согласования макета. Флеш-печати и сложные макеты — до 1 рабочего дня.'),
    ('Можно ли сделать печать по моему эскизу или логотипу?',
     'Да. Пришлите файл в любом формате (PDF, JPG, PNG, CDR, AI) или просто фото эскиза — мы подготовим макет.'),
    ('Чем автоматическая оснастка лучше ручной?',
     'В автоматической встроена штемпельная подушка: оттиск всегда ровный, руки и стол чистые, '
     'краски хватает на тысячи оттисков. Ручная дешевле, но требует отдельной подушки.'),
    ('Вы восстанавливаете печати по оттиску?',
     'Да, при наличии документов, подтверждающих право на изготовление печати.'),
    ('Есть ли доставка?',
     'Да, доставляем готовые печати по городу. Стоимость и сроки уточняйте у менеджера.'),
]

ABOUT = (
    '<p><strong>Basma Service</strong> — сервис для предпринимателей: от регистрации компании до готовой '
    'печати на столе. Мы изготавливаем печати и штампы любой сложности, ведём бухгалтерию и помогаем '
    'с получением лицензий.</p>'
    '<p>Работаем на современном лазерном оборудовании и используем оригинальные оснастки ведущих '
    'производителей. Каждый макет согласуем с клиентом, а срочные заказы выполняем за час.</p>'
)


class Command(BaseCommand):
    help = 'Стартовое наполнение сайта Basma Service'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Удалить каталог и контент перед заполнением')

    def _image(self, obj, field, filename):
        path = MEDIA / filename
        if path.exists() and not getattr(obj, field):
            with path.open('rb') as fh:
                getattr(obj, field).save(filename.replace('.png', '.webp'), File(fh), save=True)

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts['reset']:
            Product.objects.all().delete()
            Category.objects.all().delete()
            for model in (Service, Advantage, Step, FAQ):
                model.objects.all().delete()

        SiteSettings.load()

        cats = {}
        for i, (name, slug, tagline, img, desc) in enumerate(CATEGORIES):
            cat, created = Category.objects.get_or_create(
                slug=slug, defaults={'name': name, 'tagline': tagline, 'description': f'<p>{desc}</p>',
                                     'order': i})
            if created:
                self._image(cat, 'image', img)
            cats[slug] = cat

        for i, (cat, name, brand, size, shape, price, pfrom, pop, constr, short) in enumerate(PRODUCTS):
            Product.objects.get_or_create(name=name, defaults={
                'category': cats[cat], 'brand': brand, 'size': size, 'shape': shape, 'price': price,
                'price_from': pfrom, 'is_popular': pop, 'in_constructor': constr,
                'short_description': short, 'order': i,
            })

        for i, (name, slug, icon, img, short, features, price, term) in enumerate(SERVICES):
            svc, created = Service.objects.get_or_create(slug=slug, defaults={
                'name': name, 'icon': icon, 'short_description': short, 'features': features,
                'price_text': price, 'term_text': term, 'order': i,
                'description': f'<p>{short}</p>',
            })
            if created:
                self._image(svc, 'image', img)

        if not Advantage.objects.exists():
            Advantage.objects.bulk_create(
                Advantage(title=t, text=x, icon=ic, order=i) for i, (t, x, ic) in enumerate(ADVANTAGES))
        if not Step.objects.exists():
            Step.objects.bulk_create(Step(title=t, text=x, order=i) for i, (t, x) in enumerate(STEPS))
        if not FAQ.objects.exists():
            FAQ.objects.bulk_create(FAQ(question=q, answer=a, order=i) for i, (q, a) in enumerate(FAQS))

        Page.objects.get_or_create(slug='about', defaults={
            'title': 'О компании', 'lead': 'Помогаем бизнесу стартовать и работать без бумажной волокиты.',
            'content': ABOUT})
        Page.objects.get_or_create(slug='privacy', defaults={
            'title': 'Политика конфиденциальности',
            'content': '<p>Мы используем ваши имя и телефон только для связи по вашей заявке '
                       'и не передаём их третьим лицам.</p>'})

        self._apply_i18n()

        self.stdout.write(self.style.SUCCESS(
            f'Готово: {Category.objects.count()} категорий, {Product.objects.count()} товаров, '
            f'{Service.objects.count()} услуг. Цены ориентировочные — проверьте в админке.'))


def _fill(obj, **values):
    """Записывает значения только в пустые поля, затем сохраняет."""
    changed = False
    for field, value in values.items():
        if value and not getattr(obj, field):
            setattr(obj, field, value)
            changed = True
    if changed:
        obj.save()


def _apply_i18n(self):
    site = SiteSettings.load()
    # русские значения первого экрана с ключевыми словами (если не меняли вручную)
    # modeltranslation копирует default модели во все языки — такие ky-поля считаем пустыми
    for k in I18N.SITE['ky']:
        if getattr(site, f'{k}_ky') == getattr(site, f'{k}_ru'):
            setattr(site, f'{k}_ky', '')
    # старые значения по умолчанию заменяем новыми (с ключевыми словами / разметкой строк)
    old_defaults = {'hero_text': 'Изготовим печать или штамп по вашему макету',
                    'hero_title': 'Печать за 1 час. Бизнес — под ключ.'}
    for lang in ('ru', 'ky'):
        for k, marker in old_defaults.items():
            if marker in (getattr(site, f'{k}_{lang}') or ''):
                setattr(site, f'{k}_{lang}', '')
    if (site.hero_title_ky or '').startswith('Мөөр 1 саатта даяр'):
        site.hero_title_ky = ''
    _fill(site, **{f'{k}_ru': v for k, v in I18N.SITE['ru'].items()},
          **{f'{k}_ky': v for k, v in I18N.SITE['ky'].items()},
          seo_text_ru=I18N.HOME_SEO['ru'], seo_text_ky=I18N.HOME_SEO['ky'])

    for slug, d in I18N.CATEGORIES.items():
        cat = Category.objects.filter(slug=slug).first()
        if cat:
            _fill(cat, name_ky=d['name'], tagline_ky=d['tagline'], description_ky=d['description'],
                  seo_text_ru=d['seo_ru'], seo_text_ky=d['seo_ky'])

    for name_ru, (name_ky, short_ky) in I18N.PRODUCTS.items():
        for prod in Product.objects.filter(name_ru=name_ru):
            _fill(prod, name_ky=name_ky, short_description_ky=short_ky)

    for slug, d in I18N.SERVICES.items():
        svc = Service.objects.filter(slug=slug).first()
        if svc:
            _fill(svc, **{f'{k}_ky': v for k, v in d.items()},
                  description_ky=f"<p>{d['short_description']}</p>")

    for obj, (title, text) in zip(Advantage.objects.order_by('order'), I18N.ADVANTAGES):
        _fill(obj, title_ky=title, text_ky=text)
    for obj, (title, text) in zip(Step.objects.order_by('order'), I18N.STEPS):
        _fill(obj, title_ky=title, text_ky=text)
    for obj, (q, a) in zip(FAQ.objects.order_by('order'), I18N.FAQS):
        _fill(obj, question_ky=q, answer_ky=a)
    for slug, d in I18N.PAGES.items():
        page = Page.objects.filter(slug=slug).first()
        if page:
            _fill(page, **{f'{k}_ky': v for k, v in d.items()})


Command._apply_i18n = _apply_i18n
