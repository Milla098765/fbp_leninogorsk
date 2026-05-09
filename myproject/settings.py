import os
from pathlib import Path
# Путь к корню проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Безопасность
SECRET_KEY = 'django-insecure-s%@_tgl**aq8k94-^6*cq+ybj8(*8n53tzb51um$x(2h8zipwl'

# settings.py
DEBUG = False

ALLOWED_HOSTS = ['*']

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'index',  # Ваше приложение
]

# Мидлвэры
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

# Шаблоны
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'

# База данных PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'FBP',
        'USER': 'postgres',
        'PASSWORD': '88710',
        'HOST': 'localhost',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
    }
}

# Валидаторы паролей (если будете использовать стандартные)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Язык и время
LANGUAGE_CODE = 'ru-ru'  # или 'en-us'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

# Статические файлы (CSS, JS)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') 

# Медиа файлы (пользовательские фото и т.д.)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ключ по умолчанию для автоинкрементных полей
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Если вы всё еще хотите использовать стандартную аутентификацию Django,
# то нужно указать кастомную модель пользователя, но у вас кастомная модель без наследования,
# поэтому эту строку пока не добавляйте
# AUTH_USER_MODEL = 'index.Пользователь'

# Однако без наследования AbstractUser аутентификация django работать не будет.
# Для собственной аутентификации используйте свою логику во views.py
AUTHENTICATION_BACKENDS = [
    'index.backends.OrganizationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Уберите или закомментируйте если есть
# LOGIN_URL = '/organization/login/'

# Добавьте в settings.py
LOGIN_URL = '/organization/login/'

# Настройки сессий
SESSION_COOKIE_NAME = 'fbp_sessionid'
SESSION_COOKIE_DOMAIN = None
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Настройки Telegram бота (получите у @BotFather)
TELEGRAM_BOT_TOKEN = '8768391018:AAHsj2lLBVFtr1Ee7EFYiD34AstgLOzkqtE'  # Замените на реальный токен
TELEGRAM_CHAT_ID = '1203539083'      # Замените на реальный chat_id

# Email settings for Mail.ru
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mail.ru'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'kburajikina@mail.ru'  # ваша почта
EMAIL_HOST_PASSWORD = 'Tq6hvAYXWhBAOogdCrVK'  # пароль приложения
DEFAULT_FROM_EMAIL = 'kburajikina@mail.ru'