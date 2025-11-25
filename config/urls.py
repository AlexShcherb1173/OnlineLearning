"""
Главный URL-конфиг проекта OnlineLearning.

Здесь подключаются все основные маршруты:
- административная панель Django (/admin/)
- API пользователей (/api/users/)
- API курсов и уроков (/api/lms/)

Также в режиме DEBUG автоматически раздаётся MEDIA-контент,
например загруженные аватарки пользователей или превью курсов.

Этот файл — точка входа маршрутизации всего проекта.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


# -----------------------------------------------------------
# Основные маршруты проекта
# -----------------------------------------------------------
urlpatterns = [
    # Админ-панель Django
    path("admin/", admin.site.urls),

    # API пользователей (регистрация, управление профилем и др.)
    path("api/users/", include("users.urls")),

    # API системы обучения: курсы и уроки
    path("api/lms/", include("lms.urls")),
]


# -----------------------------------------------------------
# Раздача файлов MEDIA в режиме отладки
# -----------------------------------------------------------
# Когда DEBUG=True — Django сам отдаёт медиафайлы.
# В продакшене этим занимается nginx / s3 / cloud storage и т.п.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)