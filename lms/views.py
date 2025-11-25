from rest_framework import viewsets, generics

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для полной CRUD-работы с моделью Course.
    Операции:
        - GET    /courses/          — получить список всех курсов
        - POST   /courses/          — создать новый курс
        - GET    /courses/{id}/     — получить данные конкретного курса
        - PUT    /courses/{id}/     — полностью обновить данные курса
        - PATCH  /courses/{id}/     — частично обновить выбранные поля курса
        - DELETE /courses/{id}/     — удалить курс
    ViewSet выбран, потому что он обеспечивает удобный и лаконичный
    механизм для полного набора CRUD-операций, автоматически создавая
    маршруты через Router. Это делает код компактным и расширяемым,
    особенно при работе с сущностями верхнего уровня (например, курсы).
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # По условию проекта авторизацию пока не используем.


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    Представление для вывода списка уроков и создания нового урока.
    Операции:
        - GET  /lessons/  — получить список всех уроков
        - POST /lessons/  — создать новый урок
    Использование Generic ListCreateAPIView позволяет декларативно
    определить логику отображения и создания объектов Lesson без
    лишнего дублирования кода. Подходит для случаев, когда требуется
    только список + создание, без операций над конкретным объектом.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для работы с конкретным уроком по его ID.
    Операции:
        - GET    /lessons/{id}/  — получить один урок
        - PUT    /lessons/{id}/  — полностью обновить урок
        - PATCH  /lessons/{id}/  — частично обновить поля урока
        - DELETE /lessons/{id}/  — удалить урок

    Generic RetrieveUpdateDestroyAPIView обеспечивает лаконичную реализацию
    стандартного набора операций над одной сущностью Lesson. Этот класс
    идеально подходит для CRUD над объектами, которые уже существуют
    и идентифицируются по первичному ключу.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
