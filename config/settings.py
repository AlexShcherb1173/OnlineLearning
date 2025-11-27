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
    # Приложения проекта
    "users",
    "lms",
]


REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
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

LANGUAGE_CODE = "en-us"  # Можно изменить на "ru-ru"
TIME_ZONE = "UTC"
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

EMAIL_BACKEND = "django.users.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
EMAIL_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USE_TLS = os.getenv("SMTP_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.getenv("SMTP_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD", "")

"""
⚠ Важно:
EMAIL_BACKEND сейчас указан как:
    'django.users.mail.backends.smtp.EmailBackend'
Это выглядит как опечатка. Правильно должно быть:
    'django.core.mail.backends.smtp.EmailBackend'
Если не исправить — отправка почты работать не будет.
"""
