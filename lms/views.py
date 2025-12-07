from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiTypes,
    OpenApiParameter,
)
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, Subscription
from .paginators import StandardResultsSetPagination
from .serializers import CourseSerializer, LessonSerializer
from .tasks import send_course_update_notifications
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
        "DELETE - удаление урока (с учётом прав доступа).\n\n"
        "При обновлении урока дополнительно проверяется, не отправлялись ли "
        "уведомления по курсу за последние 4 часа. Если нет — запускается "
        "асинхронная рассылка писем подписчикам курса."
    ),
    tags=["Уроки"],
)
class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Представление для работы с конкретным уроком по его ID.
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

    def perform_update(self, serializer):
        """
        При обновлении урока:
        - сохраняем изменения;
        - проверяем, когда в последний раз по курсу отправлялись уведомления;
        - если не было рассылки более 4 часов — запускаем Celery-задачу
          send_course_update_notifications и обновляем last_notification_at.
        """
        lesson = serializer.save()
        course = lesson.course

        now = timezone.now()
        last_notif = course.last_notification_at
        threshold = now - timedelta(hours=4)

        should_notify = last_notif is None or last_notif <= threshold

        if should_notify:
            # Запуск асинхронной рассылки
            send_course_update_notifications.delay(course.id, lesson.id)
            # Обновляем метку последней рассылки, чтобы не слать чаще, чем раз в 4 часа
            course.last_notification_at = now
            course.save(update_fields=["last_notification_at"])


@extend_schema(
    summary="Подписка/отписка от курса",
    description=(
        "Позволяет текущему авторизованному пользователю подписаться на курс или "
        "отписаться от него.\n\n"
        "URL: `/api/lms/courses/{course_id}/subscribe/`\n"
        "Метод: `POST`\n\n"
        "- Если подписка уже существует — она **удаляется**, возвращается `message='подписка удалена'`.\n"
        "- Если подписки не было — она **создаётся**, возвращается `message='подписка добавлена'`."
    ),
    tags=["Подписки"],
    parameters=[
        OpenApiParameter(
            name="course_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.PATH,
            description="ID курса, на который выполняется подписка/отписка",
            required=True,
        ),
    ],
    request=None,  # тело запроса не ожидается
    responses={200: OpenApiTypes.OBJECT},
)
class CourseSubscriptionAPIView(APIView):
    """
    Тоггл-подписка на курс для текущего пользователя.
    URL:
        POST /api/lms/courses/<int:course_id>/subscribe/
    Логика:
      - если подписка уже существует → удаляем, возвращаем "подписка удалена"
      - если подписки нет → создаём, возвращаем "подписка добавлена"
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, course_id: int, *args, **kwargs):
        user = request.user
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