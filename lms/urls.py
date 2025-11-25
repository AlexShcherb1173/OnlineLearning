from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
)

"""
URL-конфигурация приложения lms.
Содержит маршруты для работы с курсами и уроками:
1. Курсы (CourseViewSet):
    - Генерируются автоматически через DefaultRouter.
    - Доступные эндпоинты:
        * GET    /courses/          — список курсов
        * POST   /courses/          — создание курса
        * GET    /courses/{id}/     — подробная информация о курсе
        * PUT    /courses/{id}/     — полное обновление
        * PATCH  /courses/{id}/     — частичное обновление
        * DELETE /courses/{id}/     — удаление курса
2. Уроки (GenericAPIView):
    - path("lessons/") — список и создание уроков:
        * GET  /lessons/            — список всех уроков
        * POST /lessons/            — создание нового урока
    - path("lessons/<int:pk>/") — операции над конкретным уроком:
        * GET    /lessons/{id}/     — получить урок
        * PUT    /lessons/{id}/     — полное обновление
        * PATCH  /lessons/{id}/     — частичное обновление
        * DELETE /lessons/{id}/     — удалить урок
На данном этапе проект открыт для свободного тестирования,
и авторизация не применяется.
"""

# ----------------------
# ViewSet для курсов
# ----------------------
router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")

# ----------------------
# Эндпоинты уроков
# ----------------------
urlpatterns = [
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path(
        "lessons/<int:pk>/",
        LessonRetrieveUpdateDestroyAPIView.as_view(),
        name="lesson-detail",
    ),
]

urlpatterns += router.urls
