from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from django.views.decorators.cache import cache_page
from django.views.generic import RedirectView, TemplateView

from apps.base.sitemaps import sitemaps
from apps.base.views import favicon, robots_txt
from apps.contacts.views import lead_file

# Без языкового префикса
urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path(f'{settings.ADMIN_URL}lead-file/<int:pk>/', lead_file, name='lead_file'),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('sitemap.xml', cache_page(60 * 60)(sitemap),
         {'sitemaps': sitemaps, 'template_name': 'sitemap.xml'}, name='sitemap'),
    path('robots.txt', robots_txt, name='robots'),
    path('favicon.ico', favicon),
    path('site.webmanifest', TemplateView.as_view(template_name='site.webmanifest',
                                                  content_type='application/manifest+json')),

    # Редиректы со старых адресов WordPress (кириллические slug'и и служебные)
    path('главная/', RedirectView.as_view(url='/', permanent=True)),
    path('печати/', RedirectView.as_view(url='/catalog/', permanent=True)),
    path('автоматический/', RedirectView.as_view(url='/catalog/avtomaticheskie-osnastki/', permanent=True)),
    path('ручные/', RedirectView.as_view(url='/catalog/ruchnye-osnastki/', permanent=True)),
    path('штампы/', RedirectView.as_view(url='/catalog/', permanent=True)),
    path('расходные-материалы/', RedirectView.as_view(url='/catalog/rashodnye-materialy/', permanent=True)),
    path('о-компании/', RedirectView.as_view(url='/about/', permanent=True)),
    path('контакты/', RedirectView.as_view(url='/contacts/', permanent=True)),
    path('feed/', RedirectView.as_view(url='/', permanent=True)),
    path('wp-login.php', RedirectView.as_view(url='/', permanent=True)),
]

# Русский — без префикса, кыргызский — /ky/...
urlpatterns += i18n_patterns(
    path('', include('apps.base.urls')),
    path('', include('apps.catalog.urls')),
    path('', include('apps.cms.urls')),
    path('', include('apps.contacts.urls')),
    prefix_default_language=False,
)

handler404 = 'apps.base.views.error_404'
handler500 = 'apps.base.views.error_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
