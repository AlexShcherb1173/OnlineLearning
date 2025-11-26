from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор модели User для общего CRUD.
    Используется в UserViewSet и предоставляет
    стандартное отображение данных пользователя:
    Поля:
        - id: уникальный идентификатор (только для чтения)
        - email: email пользователя (уникальный логин)
        - first_name: имя
        - last_name: фамилия
        - phone: номер телефона
        - city: город
        - avatar: путь к аватару (ImageField)
    Данный сериализатор подходит для административных операций
    (список пользователей, создание, редактирование)
    и даёт полный доступ к редактируемым пользовательским данным,
    за исключением поля id.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        ]
        read_only_fields = ["id"]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя.
    Более узкоспециализированный вариант сериализатора,
    предназначенный именно для отображения и обновления
    "профильных" данных пользователя:
    Поля:
        - id: уникальный идентификатор (только чтение)
        - email: контактный email (может редактироваться)
        - first_name: имя пользователя
        - last_name: фамилия
        - phone: номер телефона
        - city: город проживания
        - avatar: аватар пользователя
    Используется в UserProfileRetrieveUpdateAPIView и подходит
    для UPDATE/PATCH профиля без административных полей:
    без is_staff, is_superuser, groups, permissions и других
    "служебных" атрибутов.
    """

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        ]
        read_only_fields = ["id"]
