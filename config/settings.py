"""
Django settings for OnlineLearning project.
Файл содержит основные настройки проекта:
- загрузка переменных окружения через dotenv;
- конфигурация приложений;
- описание middleware;
- подключение PostgreSQL;
- локализация, работа со статикой и медиа;
- настройки email.
Данный settings.py подходит для разработки и базового деплоя.
Для продакшена необходимо:
    - изменить SECRET_KEY;
    - отключить DEBUG;
    - настроить ALLOWED_HOSTS;
    - использовать защищённые email / DB креды.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
from celery.schedules import crontab

# Загружаем переменные окружения из файла .env
load_dotenv()

# --------------------------------------------
# Базовая директория проекта
# --------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------
# Безопасность
# --------------------------------------------

# Секретный ключ Django.
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-secret-change-me")

# Режим отладки.
DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

# Разрешённые хосты (через .env: DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost)
ALLOWED_HOSTS = [h for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h]


# --------------------------------------------
# Подключённые приложения
# --------------------------------------------

INSTALLED_APPS = [
    # Базовые Django-приложения
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Сторонние приложения
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    # Приложения проекта
    "users",
    "lms",
]


REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    #    схема по умолчанию — от drf-spectacular
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Указываем кастомную модель пользователя
AUTH_USER_MODEL = "users.User"


# --------------------------------------------
# Middleware
# --------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# --------------------------------------------
# URL-конфигурация
# --------------------------------------------

ROOT_URLCONF = "config.urls"


# --------------------------------------------
# Шаблоны
# --------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],  # Можно указать дополнительные директории шаблонов
        "APP_DIRS": True,  # Django автоматически ищет templates/ внутри приложений
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# WSGI-приложение
WSGI_APPLICATION = "config.wsgi.application"


# --------------------------------------------
# Настройки базы данных
# --------------------------------------------
# Используется PostgreSQL с параметрами из .env

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "OnlineLearning_db"),
        "USER": os.getenv("POSTGRES_USER", "postgres"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "HOST": os.getenv("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}


# --------------------------------------------
# Валидация паролей
# --------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --------------------------------------------
# Интернационализация
# --------------------------------------------

LANGUAGE_CODE = os.getenv("LANGUAGE_CODE", "en-us")
TIME_ZONE = os.getenv("TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True


# --------------------------------------------
# Статические файлы: CSS, JS, изображения
# --------------------------------------------

STATIC_URL = "static/"


# --------------------------------------------
# Медиа-файлы (загружаемые пользователями изображения)
# --------------------------------------------

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# --------------------------------------------
# Первичный ключ по умолчанию
# --------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --------------------------------------------
# Email-настройки
# --------------------------------------------
# Здесь используется SMTP; все параметры должны быть в .env

EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)
EMAIL_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USE_TLS = os.getenv("SMTP_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("SMTP_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# --------------------------------------------
# Stripe
# --------------------------------------------

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# URL для редиректа после успешной / отменённой оплаты
STRIPE_SUCCESS_URL = os.getenv(
    "STRIPE_SUCCESS_URL",
    "http://127.0.0.1:8000/payments/success/",
)
STRIPE_CANCEL_URL = os.getenv(
    "STRIPE_CANCEL_URL",
    "http://127.0.0.1:8000/payments/cancel/",
)

# --------------------------------------------
# Redis (для Celery)
# --------------------------------------------

REDIS_HOST = os.getenv("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")

if REDIS_PASSWORD:
    REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
else:
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# --------------------------------------------
# Celery + celery-beat
# --------------------------------------------

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = TIME_ZONE  # тот же, что и у Django
CELERY_ENABLE_UTC = False  # работаем в локальном TIME_ZONE

# расписания для celery-beat.

CELERY_BEAT_SCHEDULE = {
    "example-every-5-minutes": {  # тестовый example_periodic_task
        "task": "lms.tasks.example_periodic_task",
        "schedule": crontab(minute="*/5"),
        "args": (),
    },
    "deactivate-inactive-users-daily": {
        "task": "users.tasks.deactivate_inactive_users",
        # каждый день в 03:00 по TIME_ZONE (Europe/Amsterdam из .env)
        "schedule": crontab(hour=3, minute=0),
        "args": (),
    },
}

# --------------------------------------------
# drf-spectacular
# --------------------------------------------

SPECTACULAR_SETTINGS = {
    "TITLE": "OnlineLearning API",
    "DESCRIPTION": (
        "API платформы онлайн обучения OnlineLearning.\n\n"
        "Содержит эндпоинты для работы с пользователями, курсами, уроками, "
        "платежами и подписками на курсы. Stripe."
    ),
    "VERSION": "1.0.0",
    # Включаем схемы в /api/schema/
    "SERVE_INCLUDE_SCHEMA": False,
    # Схема безопасности для JWT (Bearer)
    "AUTHENTICATION_WHITELIST": [],
    "COMPONENT_SPLIT_REQUEST": True,
    "SECURITY": [{"BearerAuth": []}],
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
}
