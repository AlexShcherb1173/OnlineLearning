from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CourseViewSet,
    LessonListCreateAPIView,
    LessonRetrieveUpdateDestroyAPIView,
)

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
urlpatterns = [
    # уроки через generic-классы
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path("lessons/<int:pk>/", LessonRetrieveUpdateDestroyAPIView.as_view(), name="lesson-detail"),
]

urlpatterns += router.urls