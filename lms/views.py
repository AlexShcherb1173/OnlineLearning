from rest_framework import viewsets, generics, status
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiTypes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .paginators import StandardResultsSetPagination

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModeratorOrAdmin, IsOwner


@extend_schema_view(
    list=extend_schema(
        summary="Список курсов",
        description="Возвращает список курсов с количеством и списком уроков.",
        tags=["Курсы"],
    ),
    retrieve=extend_schema(
        summary="Детальная информация о курсе",
        description=(
            "Возвращает один курс, включая количество уроков (lessons_count) "
            "и вложенный список уроков (lessons)."
        ),
        tags=["Курсы"],
    ),
    create=extend_schema(
        summary="Создать курс",
        description="Создаёт новый курс. Владелец курса устанавливается по текущему пользователю.",
        tags=["Курсы"],
    ),
    update=extend_schema(
        summary="Обновить курс",
        description="Полностью обновляет данные курса.",
        tags=["Курсы"],
    ),
    partial_update=extend_schema(
        summary="Частично обновить курс",
        description="Частично обновляет данные курса.",
        tags=["Курсы"],
    ),
    destroy=extend_schema(
        summary="Удалить курс",
        description="Удаляет курс (если права доступа позволяют).",
        tags=["Курсы"],
    ),
)
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
    pagination_class = StandardResultsSetPagination

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


@extend_schema(
    summary="Список уроков / создание урока",
    description=(
        "GET - список всех уроков (с пагинацией).\n"
        "POST - создание нового урока, автоматически привязанного к владельцу."
    ),
    tags=["Уроки"],
)
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
    pagination_class = StandardResultsSetPagination

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


@extend_schema(
    summary="Работа с конкретным уроком",
    description=(
        "GET - получение одного урока.\n"
        "PUT/PATCH - изменение урока.\n"
        "DELETE - удаление урока (с учётом прав доступа)."
    ),
    tags=["Уроки"],
)
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


@extend_schema(
    summary="Подписка/отписка от курса",
    description=(
        "Позволяет текущему авторизованному пользователю подписаться на курс или "
        "отписаться от него.\n\n"
        'Тело запроса: {"course_id": <ID курса>}.\n'
        "Если подписка была — она удаляется, возвращается message='подписка удалена'.\n"
        "Если подписки не было — она создаётся, возвращается message='подписка добавлена'."
    ),
    tags=["Подписки"],
    request={
        "application/json": {
            "type": "object",
            "properties": {"course_id": {"type": "integer"}},
        }
    },
    responses={200: OpenApiTypes.OBJECT},
)
class CourseSubscriptionAPIView(APIView):
    """
    Тоггл-подписка на курс для текущего пользователя.
    POST /api/lms/courses/subscribe/
    Ожидает в теле запроса:
    {
      "course_id": <id курса>
    }
    Логика:
      - если подписка уже существует → удаляем, возвращаем "подписка удалена"
      - если подписки нет → создаём, возвращаем "подписка добавлена"
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id") or request.data.get("course")

        if not course_id:
            return Response(
                {"detail": "Не указан course_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, pk=course_id)

        subs_qs = Subscription.objects.filter(user=user, course=course)

        if subs_qs.exists():
            subs_qs.delete()
            message = "подписка удалена"
            is_subscribed = False
        else:
            Subscription.objects.create(user=user, course=course)
            message = "подписка добавлена"
            is_subscribed = True

        return Response(
            {
                "message": message,
                "course_id": course.id,
                "is_subscribed": is_subscribed,
            },
            status=status.HTTP_200_OK,
        )
