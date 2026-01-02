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
from django.http import HttpResponse
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from users.views import RegisterAPIView


# -----------------------------------------------------------
# Основные маршруты проекта
# -----------------------------------------------------------
urlpatterns = [
    path("", lambda request: HttpResponse("OK")),
    # Админ-панель Django
    path("admin/", admin.site.urls),
    # API пользователей (регистрация, управление профилем и др.)
    # JWT авторизация
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Регистрация пользователя (доступна без токена)
    path("api/auth/register/", RegisterAPIView.as_view(), name="user-register"),
    path("api/users/", include("users.urls")),
    # API системы обучения: курсы и уроки
    path("api/lms/", include("lms.urls")),
    # схема OpenAPI (json/yaml)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # ReDoc
    path(
        "api/docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]


# -----------------------------------------------------------
# Раздача файлов MEDIA в режиме отладки
# -----------------------------------------------------------
# Когда DEBUG=True — Django сам отдаёт медиафайлы.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
