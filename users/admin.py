from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Payment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Административная конфигурация кастомной модели User.
    Данный класс расширяет стандартный Django UserAdmin,
    адаптируя его под кастомную модель пользователя,
    в которой используется email в качестве основного идентификатора
    и добавлены дополнительные поля профиля.
    Основные настройки:
    fieldsets:
        Определяет группы полей в форме редактирования пользователя:
            - Основные данные (email и пароль)
            - Личная информация (имя, фамилия, телефон, город, аватар)
            - Права доступа (статусы, группы, разрешения)
            - Важные даты (последний вход, дата регистрации)
    add_fieldsets:
        Конфигурация отображения формы создания нового пользователя в админке.
        Использует только email и два поля пароля.
    list_display:
        Поля, отображаемые в списке пользователей:
            id, email, имя, фамилия, флаг is_staff.
    list_filter:
        Фильтры справа в списке пользователей:
            права, статус активности, статус суперпользователя, группы.
    search_fields:
        Позволяет искать пользователей по email, имени и фамилии.
    ordering:
        Сортировка пользователей в списке — по полю email.
    Итог:
        Эта конфигурация делает работу с кастомной моделью User в Django Admin
        полностью аналогичной стандартной, но с расширенными полями профиля
        и авторизацией по email.
    """

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {"fields": ("first_name", "last_name", "phone", "city", "avatar")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )

    list_display = ("id", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Payment.
    Позволяет просматривать и фильтровать платежи за курсы и уроки.
    Основные возможности:
        - список платежей с ключевой информацией:
          пользователь, курс/урок, сумма, способ оплаты, дата
        - фильтрация по пользователю, курсу, уроку и способу оплаты
        - поиск по email пользователя и названию курса/урока
        - удобная навигация по дате оплаты (date_hierarchy)
    """

    list_display = (
        "id",
        "user",
        "course",
        "lesson",
        "amount",
        "payment_method",
        "paid_at",
    )
    list_filter = (
        "payment_method",
        "course",
        "lesson",
        "user",
        "paid_at",
    )
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "course__title",
        "lesson__title",
    )
    date_hierarchy = "paid_at"
    ordering = ("-paid_at",)
