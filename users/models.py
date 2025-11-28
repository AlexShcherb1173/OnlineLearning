from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.db.models import Q, CheckConstraint

from lms.models import Course, Lesson


class User(AbstractUser):
    """
    Кастомная модель пользователя для проекта OnlineLearning.
    Расширяет стандартную модель Django `AbstractUser`, оставляя все её поля,
    но изменяет механизм аутентификации и добавляет дополнительные
    пользовательские атрибуты.
    Основные отличия от стандартного пользователя:
    1. Авторизация по email:
        - Поле email становится уникальным.
        - Поле username сохраняется, но делается необязательным.
        - USERNAME_FIELD установлен в "email".
        - REQUIRED_FIELDS пуст — при создании суперпользователя будет
          запрошен только email и пароль.
    2. Дополнительные поля профиля:
        - phone: контактный номер телефона
        - city: город проживания
        - avatar: изображение аватара, загружаемое в media/users/avatars/
    Поведение:
        - __str__ возвращает email пользователя (удобно для админки).
        - Модель объявлена в settings.py как AUTH_USER_MODEL.
    """

    # Делаем username необязательным — он остаётся в модели,
    # что упрощает совместимость, но не используется для авторизации.
    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
        null=True,
        verbose_name="Имя пользователя",
    )

    # Уникальный email — ключевой идентификатор.
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
    )

    # Дополнительные поля профиля
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

    # Настройки аутентификации
    USERNAME_FIELD = "email"  # Используем email вместо username
    REQUIRED_FIELDS = (
        []
    )  # Не требуем username, first_name и др. при создании суперпользователя

    def __str__(self):
        """Возвращаем email пользователя для удобного отображения в админке."""
        return self.email or super().__str__()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    """
    Платёж за курс или урок.
    Поля:
        user        — пользователь, совершивший оплату (FK на кастомную модель User)
        paid_at     — дата и время оплаты
        course      — оплаченный курс (может быть пустым, если оплачен только урок)
        lesson      — оплаченный урок (может быть пустым, если оплачен только курс)
        amount      — сумма оплаты
        payment_method — способ оплаты (наличные или перевод на счёт)
    Важно:
        - хотя по формулировке "оплаченный курс или урок" подразумевается
          взаимоисключающий выбор, в модели оставляем оба поля с возможностью null.
          Логика "либо курс, либо урок" может контролироваться на уровне бизнес-логики.
    """

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Наличные"
        TRANSFER = "transfer", "Перевод на счёт"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )

    paid_at = models.DateTimeField(
        verbose_name="Дата и время оплаты",
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

    def __str__(self):
        target = self.course or self.lesson
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
