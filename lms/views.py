from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModeratorOrAdmin, IsOwner


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
    Права доступа:
      - list, retrieve: любой аутентифицированный пользователь
     - update/partial_update: модератор или владелец (или админ)
      - create, destroy: только администраторы (модераторы не могут)
    """

    queryset = Course.objects.all().prefetch_related("lessons")
    serializer_class = CourseSerializer

    def get_queryset(self):
        """
        Немодератор/неадмин видит только свои курсы.
        Модератор и админ — все.
        """
        user = self.request.user
        qs = Course.objects.all()

        if not user.is_authenticated:
            return qs.none()

        is_moderator = user.groups.filter(name="moderators").exists()
        is_admin = user.is_staff or user.is_superuser

        if is_moderator or is_admin:
            return qs
        return qs.filter(owner=user)

    def get_permissions(self):
        if self.action in ("create", "destroy"):
            # создавать/удалять курсы могут только админы
            permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ("update", "partial_update"):
            # редактировать: модератор или владелец (или админ)
            permission_classes = [IsAuthenticated, IsModeratorOrAdmin | IsOwner]
        else:
            # list, retrieve — аутентифицированные
            permission_classes = [IsAuthenticated]

        return [perm() for perm in permission_classes]

    def perform_create(self, serializer):
        """
        При создании курса автоматически назначаем владельцем
        текущего пользователя.
        """
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """
    Представление для вывода списка уроков и создания нового урока.
    Операции:
       - GET /lessons/  — список уроков (аутентифицированные)
       - POST /lessons/ — создать урок (только админ, владелец будет request.user)
    Использование Generic ListCreateAPIView позволяет декларативно
    определить логику отображения и создания объектов Lesson без
    лишнего дублирования кода. Подходит для случаев, когда требуется
    только список + создание, без операций над конкретным объектом.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Lesson.objects.all()

        if not user.is_authenticated:
            return qs.none()

        is_moderator = user.groups.filter(name="moderators").exists()
        is_admin = user.is_staff or user.is_superuser

        if is_moderator or is_admin:
            return qs
        return qs.filter(owner=user)

    def get_permissions(self):
        if self.request.method == "POST":
            # создать урок может только админ
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]
        return [perm() for perm in permission_classes]

    def perform_create(self, serializer):
        """
        При создании урока привязываем его к текущему пользователю.
        """
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для работы с конкретным уроком по его ID.
    Операции:
       - GET    /lessons/{id}/ — получить урок (авторизованный пользователь)
       - PUT    /lessons/{id}/ — изменить (модератор или владелец/админ)
       - PATCH  /lessons/{id}/ — частично изменить (модератор или владелец/админ)
       - DELETE /lessons/{id}/ — удалить (только админ)
    Generic RetrieveUpdateDestroyAPIView обеспечивает лаконичную реализацию
    стандартного набора операций над одной сущностью Lesson. Этот класс
    идеально подходит для CRUD над объектами, которые уже существуют
    и идентифицируются по первичному ключу.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        method = self.request.method

        if method in ("PUT", "PATCH"):
            # редактировать может модератор или владелец (или админ)
            permission_classes = [IsAuthenticated, IsModeratorOrAdmin | IsOwner]
        elif method == "DELETE":
            # удалить — только админ
            permission_classes = [IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [IsAuthenticated]

        return [perm() for perm in permission_classes]
