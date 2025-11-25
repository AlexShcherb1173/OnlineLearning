from rest_framework import viewsets, generics
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    Полный CRUD для модели Course:
    - GET /courses/        — список
    - POST /courses/       — создание
    - GET /courses/{id}/   — детальный просмотр
    - PUT /courses/{id}/   — полное обновление
    - PATCH /courses/{id}/ — частичное обновление
    - DELETE /courses/{id}/ — удаление
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permissions не задаём, по умолчанию AllowAny


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /lessons/  — список уроков
    POST /lessons/ — создание нового урока
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /lessons/{id}/ — получить один урок
    PUT    /lessons/{id}/ — полное изменение
    PATCH  /lessons/{id}/ — частичное изменение
    DELETE /lessons/{id}/ — удалить
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer