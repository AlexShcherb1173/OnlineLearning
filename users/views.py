from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import User, Payment
from users.permissions import IsProfileOwner
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    PaymentSerializer,
    UserRegisterSerializer,
    UserPublicSerializer,
)


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
    Просмотр профиля (любой пользователь видит)
    Редактирование — только владелец профиля
    Публичные поля при просмотре чужого профиля
    """

    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = "pk"
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def get_serializer_class(self):
        """
        Если пользователь смотрит СВОЙ профиль → полный сериализатор.
        Если чужой → публичный сериализатор.
        """
        user = self.request.user
        obj = self.get_object()

        if obj == user:
            return UserProfileSerializer
        return UserPublicSerializer


class PaymentListAPIView(generics.ListAPIView):
    """
    Эндпоинт для вывода списка платежей с фильтрацией и сортировкой.
    Поддерживаемые query-параметры:
      - ?course=<id>          — фильтрация по курсу
      - ?lesson=<id>          — фильтрация по уроку
      - ?payment_method=...   — фильтрация по способу оплаты
                               (значения: "cash", "transfer")
      - ?ordering=paid_at     — сортировка по дате оплаты по возрастанию
      - ?ordering=-paid_at    — сортировка по дате оплаты по убыванию
    Примеры:
        GET /api/users/payments/
        GET /api/users/payments/?course=1
        GET /api/users/payments/?lesson=3&payment_method=cash
        GET /api/users/payments/?payment_method=transfer&ordering=paid_at
    """

    queryset = Payment.objects.select_related("user", "course", "lesson")
    serializer_class = PaymentSerializer

    # DRF + django-filter backends
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    # по этим полям можно фильтровать
    # /api/users/payments/?course=1&lesson=2&payment_method=cash
    filterset_fields = ["course", "lesson", "payment_method"]

    # по этим полям можно сортировать: ?ordering=paid_at или ?ordering=-paid_at
    ordering_fields = ["paid_at"]

    # сортировка по умолчанию: самые свежие платежи сверху
    ordering = ["-paid_at"]


class RegisterAPIView(generics.CreateAPIView):
    """
    Эндпоинт регистрации нового пользователя.
    Доступен без авторизации:
    POST /api/users/register/
    Ожидает:
    {
      "email": "user@example.com",
      "password": "strong_password",
      "first_name": "Имя",
      "last_name": "Фамилия",
      "phone": "+3100000000",
      "city": "Amsterdam"
    }
    """

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]
