import os

from core.settings.base import *  # noqa: F401,F403

DEBUG = False

# Cookies только по HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Приложение работает за nginx, который терминирует HTTPS.
# Без этого Django считает запрос http-запросом и ломает CSRF/редиректы.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

# Прочие security-заголовки
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin'
CSRF_COOKIE_HTTPONLY = True        # токен берём из скрытого поля формы, JS cookie не читает
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 12  # сессия админки — 12 часов

# HSTS: включайте только когда HTTPS точно работает (значение задаётся в .env),
# иначе браузеры запомнят домен и http перестанет открываться.
SECURE_HSTS_SECONDS = int(os.getenv('SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Редирект на HTTPS делает nginx
SECURE_SSL_REDIRECT = False
SILENCED_SYSTEM_CHECKS = ['ckeditor.W001', 'security.W008']

# =============================================================================
# LOGGING — при DEBUG=False ошибки иначе уходят в никуда
# =============================================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# Хеши в именах статики (main.3f9a1c.css) — браузеры кэшируют надолго,
# а после деплоя сразу получают новую версию.
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'},
}
