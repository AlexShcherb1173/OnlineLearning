from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Кастомный пользователь:
    - логинимся по email
    - добавлены телефон, город, аватар
    """

    # делаем username необязательным (но поле остаётся, как просили — "все поля от обычного пользователя")
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

    USERNAME_FIELD = "email"      # авторизация по email
    REQUIRED_FIELDS = []          # при createsuperuser ничего дополнительно не спрашиваем

    def __str__(self):
        return self.email or super().__str__()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"