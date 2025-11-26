from django.contrib.auth.models import AbstractUser
from django.db import models


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
