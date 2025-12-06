from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import Q, CheckConstraint

from lms.models import Course, Lesson


class User(AbstractUser):
    """
    Кастомная модель пользователя для проекта OnlineLearning.
    Авторизация по email, username необязателен.
    """

    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        null=True,
        verbose_name="Имя пользователя",
    )

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Телефон",
        help_text="Контактный телефон пользователя",
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Город",
    )

    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or super().__str__()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    """
    Платёж за курс или урок.

    Ровно один из двух FK:
      - либо course не NULL и lesson NULL
      - либо course NULL и lesson не NULL
    """

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод на счёт"

    # Алиасы, чтобы можно было писать Payment.PAYMENT_METHOD_CASH / TRANSFER
    PAYMENT_METHOD_CASH = PaymentMethod.CASH
    PAYMENT_METHOD_TRANSFER = PaymentMethod.TRANSFER

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )

    paid_at = models.DateTimeField(
        verbose_name="Дата и время оплаты",
        null=True,
        blank=True,
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный курс",
    )

    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный урок",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name="Способ оплаты",
    )

    # --- Stripe-поля ---
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID продукта в Stripe",
        help_text="stripe.Product.id",
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID цены в Stripe",
        help_text="stripe.Price.id",
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии Checkout",
        help_text="stripe.CheckoutSession.id",
    )
    stripe_checkout_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату в Stripe",
    )

    # --- Статус оплаты ---
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Ожидает оплаты"),
        (STATUS_PAID, "Оплачен"),
        (STATUS_CANCELED, "Отменён"),
    ]

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name="Статус платежа",
    )

    def __str__(self):
        target = self.course or self.lesson or "неизвестный объект"
        return f"Платёж #{self.pk} от {self.user} за {target} на {self.amount}"

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-paid_at"]
        constraints = [
            CheckConstraint(
                check=(
                    (Q(course__isnull=False) & Q(lesson__isnull=True))
                    | (Q(course__isnull=True) & Q(lesson__isnull=False))
                ),
                name="payment_has_exactly_one_target",
            )
        ]
