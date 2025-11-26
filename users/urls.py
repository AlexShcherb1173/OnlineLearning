from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    UserViewSet,
    UserProfileRetrieveUpdateAPIView,
    PaymentListAPIView,
)

"""
URL-конфигурация приложения users.
Содержит два основных набора маршрутов:
1. ViewSet пользователей (UserViewSet) — полный CRUD:
   - GET    /api/users/           — список пользователей
   - POST   /api/users/           — создание пользователя
   - GET    /api/users/<id>/      — получение конкретного пользователя
   - PUT    /api/users/<id>/      — полное обновление
   - PATCH  /api/users/<id>/      — частичное обновление
   - DELETE /api/users/<id>/      — удаление
2. Эндпоинт профиля пользователя (Retrieve/Update):
   - GET    /api/users/profiles/<id>/   — получить профиль пользователя
   - PUT    /api/users/profiles/<id>/   — полностью обновить профиль
   - PATCH  /api/users/profiles/<id>/   — частично обновить профиль
На данном этапе проект открыт для свободного тестирования —
авторизация и разграничение прав пока не используются.
"""

# ----------------------
# ViewSet пользователей
# ----------------------
router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

# ----------------------
# Эндпоинт профиля
# ----------------------
urlpatterns = [
    path(
        "profiles/<int:pk>/",
        UserProfileRetrieveUpdateAPIView.as_view(),
        name="user-profile-detail",
    ),
    path(
        "payments/",
        PaymentListAPIView.as_view(),
        name="payment-list",
    ),
]

urlpatterns += router.urls
