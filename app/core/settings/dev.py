from core.settings.base import *

DEBUG = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Разрешаем iframe с того же origin — удобно смотреть мобильную вёрстку
X_FRAME_OPTIONS = 'SAMEORIGIN'
