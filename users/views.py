from rest_framework import viewsets, generics
from rest_framework.request import Request

from .models import User, Payment
from .serializers import UserSerializer, UserProfileSerializer, PaymentSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями.
    Данный класс предоставляет полный CRUD-набор операций для работы
    с моделью пользователя:
    - GET    /api/users/          — получить список всех пользователей
    - POST   /api/users/          — создать нового пользователя
    - GET    /api/users/<id>/     — получить данные одного пользователя
    - PUT    /api/users/<id>/     — полное обновление записи пользователя
    - PATCH  /api/users/<id>/     — частичное обновление
    - DELETE /api/users/<id>/     — удалить пользователя
    На данном этапе проекта доступ открыт без авторизации,
    что упрощает тестирование и наполнение базы данных.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Представление для просмотра и редактирования профиля конкретного пользователя.
    Поддерживаемые операции:
    - GET    /api/users/profiles/<id>/   — получить данные профиля пользователя
    - PUT    /api/users/profiles/<id>/   — полная замена всех полей профиля
    - PATCH  /api/users/profiles/<id>/   — частичное обновление выбранных полей
    Это удобный и лаконичный механизм редактирования именно "профильной"
    информации пользователя — имени, города, телефона и аватарки.
    Используется Generic-класс DRF, поскольку он более точечно отражает
    логику обновления одного объекта и делает код чище.

    На текущем этапе доступ открыт без авторизации, что соответствует
    условиям задачи (позже можно добавить проверку владельца профиля).
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"


class PaymentListAPIView(generics.ListAPIView):
    """
    Эндпоинт для вывода списка платежей с фильтрацией и сортировкой.
    Поддерживаемые query-параметры:
    - ?course=<id>          — фильтрация по курсу
    - ?lesson=<id>          — фильтрация по уроку
    - ?payment_method=...   — фильтрация по способу оплаты
                              (значения: "cash", "transfer")
    - ?ordering=paid_at     — сортировка по дате оплаты (по возрастанию)
    - ?ordering=-paid_at    — сортировка по дате оплаты (по убыванию)
    Примеры:
        GET /api/users/payments/
        GET /api/users/payments/?course=1
        GET /api/users/payments/?lesson=3&payment_method=cash
        GET /api/users/payments/?payment_method=transfer&ordering=paid_at
    """

    serializer_class = PaymentSerializer

    def get_queryset(self):
        request: Request = self.request
        qs = Payment.objects.select_related("user", "course", "lesson")

        # фильтрация по курсу
        course_id = request.query_params.get("course")
        if course_id:
            qs = qs.filter(course_id=course_id)

        # фильтрация по уроку
        lesson_id = request.query_params.get("lesson")
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)

        # фильтрация по способу оплаты
        payment_method = request.query_params.get("payment_method")
        if payment_method:
            qs = qs.filter(payment_method=payment_method)

        # сортировка по дате
        ordering = request.query_params.get("ordering")
        if ordering in ("paid_at", "-paid_at"):
            qs = qs.order_by(ordering)
        else:
            # по умолчанию — самые свежие платежи сверху
            qs = qs.order_by("-paid_at")

        return qs
