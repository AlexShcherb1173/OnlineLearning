from decimal import Decimal
import stripe

from django.conf import settings
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, permissions, viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes

from lms.models import Course, Lesson
from .models import User, Payment
from users.permissions import IsProfileOwner
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    PaymentSerializer,
    UserRegisterSerializer,
    UserPublicSerializer,
)
from .services.stripe_service import (
    create_stripe_product,
    create_stripe_price,
    create_checkout_session,
    retrieve_checkout_session,
)


@extend_schema_view(
    list=extend_schema(
        summary="Список пользователей",
        description="Возвращает список пользователей (для админских задач).",
        tags=["Пользователи"],
    ),
    retrieve=extend_schema(
        summary="Детали пользователя",
        description="Получение полной информации о пользователе (при наличии прав).",
        tags=["Пользователи"],
    ),
    create=extend_schema(
        summary="Регистрация пользователя (если реализовано через ViewSet.create)",
        description="Создание нового пользователя.",
        tags=["Пользователи"],
    ),
    update=extend_schema(
        summary="Обновление пользователя",
        description="Полное обновление данных пользователя.",
        tags=["Пользователи"],
    ),
    partial_update=extend_schema(
        summary="Частичное обновление пользователя",
        description="Частичное обновление данных пользователя.",
        tags=["Пользователи"],
    ),
    destroy=extend_schema(
        summary="Удаление пользователя",
        description="Удаление пользователя (обычно только для админа).",
        tags=["Пользователи"],
    ),
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
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


@extend_schema(
    summary="Профиль пользователя",
    description=(
        "GET: просмотр профиля пользователя.\n"
        "- Если запрашивающий == владелец профиля — возвращается полная информация, "
        "включая историю платежей.\n"
        "- Если запрашивающий другой пользователь — возвращается только публичная часть профиля "
        "(без фамилии, пароля, истории платежей).\n\n"
        "PUT/PATCH: редактирование доступно только владельцу профиля."
    ),
    tags=["Пользователи"],
)
class UserProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    Представление для просмотра и редактирования профиля конкретного пользователя.
    Поддерживаемые операции:
    - GET    /api/users/profiles/<id>/   — получить данные профиля пользователя
    - PUT    /api/users/profiles/<id>/   — полная замена всех полей профиля
    - PATCH  /api/users/profiles/<id>/   — частичное обновление выбранных полей

    Просмотр профиля — любой авторизованный пользователь.
    Редактирование — только владелец профиля.
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


@extend_schema(
    tags=["Платежи"],
    summary="Список платежей",
    description=(
        "Возвращает список платежей с возможностью фильтрации и сортировки.\n\n"
        "Поддерживаемые query-параметры:\n"
        "- `course` — ID курса, по которому фильтруются платежи\n"
        "- `lesson` — ID урока, по которому фильтруются платежи\n"
        "- `payment_method` — способ оплаты (`cash` — наличные, `transfer` — перевод)\n"
        "- `ordering` — сортировка по дате оплаты: `paid_at` или `-paid_at`\n\n"
        "Примеры запросов:\n"
        "- `GET /api/users/payments/all/`\n"
        "- `GET /api/users/payments/all/?course=1`\n"
        "- `GET /api/users/payments/all/?lesson=3&payment_method=cash`\n"
        "- `GET /api/users/payments/all/?payment_method=transfer&ordering=-paid_at`"
    ),
    parameters=[
        OpenApiParameter(
            name="course",
            description="ID курса для фильтрации платежей",
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="lesson",
            description="ID урока для фильтрации платежей",
            required=False,
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="payment_method",
            description="Способ оплаты: `cash` (наличные) или `transfer` (перевод)",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="ordering",
            description="Сортировка по дате оплаты: `paid_at` или `-paid_at`",
            required=False,
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
        ),
    ],
    responses={
        200: OpenApiResponse(
            response=PaymentSerializer(many=True),
            description="Список платежей с учётом фильтров и сортировки.",
        ),
        401: OpenApiResponse(description="Неавторизован."),
    },
    examples=[
        OpenApiExample(
            "Фильтрация по курсу",
            summary="Платежи по конкретному курсу",
            value={"course": 1},
        ),
        OpenApiExample(
            "Фильтрация по способу оплаты и сортировка",
            summary="Безнал по убыванию даты",
            value={"payment_method": "transfer", "ordering": "-paid_at"},
        ),
    ],
)
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
    """

    queryset = Payment.objects.select_related("user", "course", "lesson")
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    # DRF + django-filter backends
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]

    # по этим полям можно фильтровать
    filterset_fields = ["course", "lesson", "payment_method"]

    # по этим полям можно сортировать: ?ordering=paid_at или ?ordering=-paid_at
    ordering_fields = ["paid_at"]

    # сортировка по умолчанию: самые свежие платежи сверху
    ordering = ["-paid_at"]


@extend_schema(
    tags=["Пользователи"],
    summary="Регистрация нового пользователя",
    description=(
        "Создаёт нового пользователя в системе.\n\n"
        "Пример запроса:\n"
        "```json\n"
        "{\n"
        '  "email": "user@example.com",\n'
        '  "password": "strong_password",\n'
        '  "first_name": "Имя",\n'
        '  "last_name": "Фамилия",\n'
        '  "phone": "+3100000000",\n'
        '  "city": "Amsterdam"\n'
        "}\n"
        "```"
    ),
    request=UserRegisterSerializer,
    responses={
        201: OpenApiResponse(
            response=UserSerializer, description="Пользователь создан."
        ),
        400: OpenApiResponse(description="Ошибки валидации."),
    },
)
class RegisterAPIView(generics.CreateAPIView):
    """
    Эндпоинт регистрации нового пользователя.
    Доступен без авторизации: POST /api/users/register/
    """

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class StripeCheckoutCreateAPIView(APIView):
    """
    Создание Stripe Checkout-сессии для оплаты курса или урока.

    POST /api/users/payments/stripe-checkout/

    В теле запроса нужно передать либо `course_id`, либо `lesson_id`,
    а также `amount` и при необходимости `currency`.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Stripe", "Платежи"],
        summary="Создать Stripe Checkout Session",
        description=(
            "Создаёт сессию оплаты в Stripe для указанного курса или урока.\n\n"
            "Примеры запросов:\n"
            "```json\n"
            "{\n"
            '  "course_id": 1,\n'
            '  "amount": "1000.00",\n'
            '  "currency": "usd"\n'
            "}\n"
            "```\n\n"
            "```json\n"
            "{\n"
            '  "lesson_id": 5,\n'
            '  "amount": "100.00",\n'
            '  "currency": "usd"\n'
            "}\n"
            "```\n\n"
            "В ответ возвращает данные созданного платежа в системе и URL для перехода "
            "на платёжную страницу Stripe."
        ),
        request=OpenApiTypes.OBJECT,
        responses={
            201: OpenApiResponse(
                description="Сессия Stripe успешно создана. Возвращаем платёж и ссылку на оплату.",
                examples=[
                    OpenApiExample(
                        "Успешный ответ",
                        value={
                            "payment": {
                                "id": 123,
                                "user": 1,
                                "course": 10,
                                "lesson": None,
                                "amount": "1000.00",
                                "payment_method": "transfer",
                                "status": "pending",
                                "stripe_session_id": "cs_test_a1B2C3",
                                "stripe_checkout_url": "https://checkout.stripe.com/pay/cs_test_a1B2C3",
                            },
                            "checkout_url": "https://checkout.stripe.com/pay/cs_test_a1B2C3",
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="Ошибка валидации (нет amount, оба id, или ни одного и т.п.)",
                examples=[
                    OpenApiExample(
                        "Нет amount",
                        value={"detail": "Поле 'amount' обязательно."},
                    ),
                    OpenApiExample(
                        "Нет course_id и lesson_id",
                        value={
                            "detail": "Нужно передать либо 'course_id', либо 'lesson_id'."
                        },
                    ),
                    OpenApiExample(
                        "Оба id переданы",
                        value={
                            "detail": "Нельзя одновременно передать 'course_id' и 'lesson_id'."
                        },
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="Курс или урок не найден.",
            ),
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")
        lesson_id = request.data.get("lesson_id")
        amount = request.data.get("amount")
        currency = request.data.get("currency", "usd")

        if not amount:
            return Response(
                {"detail": "Поле 'amount' обязательно."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            amount = Decimal(amount)
        except Exception:
            return Response(
                {"detail": "Некорректное значение 'amount'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not course_id and not lesson_id:
            return Response(
                {"detail": "Нужно передать либо 'course_id', либо 'lesson_id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if course_id and lesson_id:
            return Response(
                {"detail": "Нельзя одновременно передать 'course_id' и 'lesson_id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = None
        lesson = None
        product_name = "Оплата"

        if course_id:
            course = get_object_or_404(Course, pk=course_id)
            product_name = f"Курс: {course.title}"
        elif lesson_id:
            lesson = get_object_or_404(Lesson, pk=lesson_id)
            product_name = f"Урок: {lesson.title}"

        # 1. Создаём Payment в нашей БД (без Stripe-полей пока)
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            payment_method=Payment.PaymentMethod.TRANSFER,  # используем TextChoices
            course=course,
            lesson=lesson,
            status=Payment.STATUS_PENDING,
        )

        # 2. Stripe: создаём product + price + session
        product = create_stripe_product(name=product_name)
        price = create_stripe_price(
            product_id=product.id,
            amount=float(amount),
            currency=currency,
        )
        session = create_checkout_session(
            price_id=price.id,
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
        )

        # 3. Сохраняем данные Stripe в Payment
        payment.stripe_product_id = product.id
        payment.stripe_price_id = price.id
        payment.stripe_session_id = session.id
        payment.stripe_checkout_url = session.url
        payment.save(
            update_fields=[
                "stripe_product_id",
                "stripe_price_id",
                "stripe_session_id",
                "stripe_checkout_url",
            ]
        )

        serializer = PaymentSerializer(payment)
        return Response(
            {
                "payment": serializer.data,
                "checkout_url": session.url,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    summary="Проверка статуса Stripe-платежа",
    description=(
        "Возвращает информацию о Stripe Checkout-сессии, привязанной к платежу, "
        "и при необходимости обновляет статус платежа в нашей системе.\n\n"
        "Логика маппинга статусов:\n"
        "- session.status == 'complete' и payment_status == 'paid' → PAYMENT.status = 'paid'\n"
        "- session.status in ['expired', 'canceled'] → PAYMENT.status = 'canceled'\n"
    ),
    tags=["Платежи", "Stripe"],
    parameters=[
        OpenApiParameter(
            name="pk",
            description="ID платежа в нашей системе (Payment.id)",
            required=True,
            type=int,
            location=OpenApiParameter.PATH,
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Успешное получение статуса платежа и сессии Stripe"
        ),
        400: OpenApiResponse(
            description="У платежа нет привязанной Stripe-сессии или ошибка в запросе"
        ),
        404: OpenApiResponse(description="Платеж не найден"),
        502: OpenApiResponse(
            description="Ошибка при обращении к Stripe (проблема на стороне внешнего сервиса)"
        ),
    },
)
class StripePaymentStatusAPIView(APIView):
    """
    Получение статуса платежа по нашему Payment.id.
    GET /api/users/payments/stripe-status/<int:pk>/
    Возвращает данные сессии Stripe и текущий статус платежа в нашей системе.
    """

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Stripe", "Платежи"],
        summary="Статус Stripe-платежа",
        description=(
            "Возвращает информацию о Stripe-сессии и статус платежа в нашей системе.\n\n"
            "Параметры:\n"
            "- `pk` — ID локального платежа (Payment.id)\n\n"
            "Если у платежа нет привязанной Stripe-сессии, вернётся ошибка 400."
        ),
        responses={
            200: OpenApiResponse(
                description="Информация о Stripe-сессии и статусе локального платежа.",
                examples=[
                    OpenApiExample(
                        "Успешный платёж",
                        value={
                            "stripe_session": {
                                "id": "cs_test_a1B2C3",
                                "url": "https://checkout.stripe.com/pay/cs_test_a1B2C3",
                                "status": "complete",
                                "payment_status": "paid",
                            },
                            "payment_status": "paid",
                        },
                    )
                ],
            ),
            400: OpenApiResponse(
                description="У платежа нет привязанной Stripe-сессии.",
                examples=[
                    OpenApiExample(
                        "Нет сессии",
                        value={
                            "detail": "У этого платежа нет привязанной Stripe-сессии."
                        },
                    )
                ],
            ),
            404: OpenApiResponse(
                description="Платеж не найден или не принадлежит текущему пользователю.",
            ),
        },
    )
    def get(self, request, pk: int, *args, **kwargs):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)

        if not payment.stripe_session_id:
            return Response(
                {"detail": "У этого платежа нет привязанной Stripe-сессии."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # аккуратно ходим в Stripe и обрабатываем ошибки
        try:
            session = retrieve_checkout_session(payment.stripe_session_id)
        except stripe.error.StripeError as e:
            return Response(
                {
                    "detail": "Ошибка при обращении к Stripe.",
                    "stripe_error": str(e),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # у объекта Session поля доступны как атрибуты
        stripe_status = session.status
        stripe_payment_status = session.payment_status

        # маппинг статусов Stripe -> наш статус
        if (
            stripe_status == "complete"
            and stripe_payment_status == "paid"
            and payment.status != Payment.STATUS_PAID
        ):
            payment.status = Payment.STATUS_PAID
            payment.save(update_fields=["status"])
        elif (
            stripe_status in ("expired", "canceled")
            and payment.status != Payment.STATUS_CANCELED
        ):
            payment.status = Payment.STATUS_CANCELED
            payment.save(update_fields=["status"])

        return Response(
            {
                "stripe_session": {
                    "id": session.id,
                    "url": getattr(session, "url", None),
                    "status": stripe_status,
                    "payment_status": stripe_payment_status,
                },
                "payment_status": payment.status,
            }
        )
