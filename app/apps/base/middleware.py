from urllib.parse import urlsplit

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """301 с www.basma.kg на основной домен из SITE_URL.

    Поисковики считают www и без www разными сайтами — без склейки
    вес страниц делится между дублями. В DEBUG не срабатывает.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        target = urlsplit(settings.SITE_URL)
        self.scheme = target.scheme or 'https'
        self.host = target.hostname or ''

    def __call__(self, request):
        if not settings.DEBUG and self.host:
            host = request.get_host().split(':')[0].lower()
            if host == f'www.{self.host}':
                return HttpResponsePermanentRedirect(
                    f'{self.scheme}://{self.host}{request.get_full_path()}')
        return self.get_response(request)


class SecurityHeadersMiddleware:
    """Заголовки, которых нет в SecurityMiddleware Django."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), payment=()')
        return response
