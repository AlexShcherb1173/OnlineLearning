from rest_framework import serializers

from .models import User, Payment


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


class PaymentSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Payment.
    Используется для:
    - списка платежей (/api/users/payments/)
    - вложенного вывода истории платежей в профиле пользователя.
    Поля:
        id            — идентификатор платежа
        user          — пользователь, совершивший оплату
        paid_at       — дата и время оплаты
        course        — оплаченный курс (может быть null)
        lesson        — оплаченный урок (может быть null)
        amount        — сумма
        payment_method — способ оплаты: "cash" или "transfer"
    """

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "paid_at",
            "course",
            "lesson",
            "amount",
            "payment_method",
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
    Используется в UserProfileRetrieveUpdateAPIView для:
    - просмотра и редактирования профильных данных пользователя;
    - вывода истории платежей пользователя (вложенный список payments).
    """

    # история платежей пользователя (related_name="payments" в модели Payment)
    payments = PaymentSerializer(many=True, read_only=True)

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
            "payments",
        ]
        read_only_fields = ["id"]

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации новых пользователей.
    При создании:
    - хэширует пароль через set_password
    - создаёт пользователя с email в качестве логина.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        help_text="Пароль (минимум 8 символов)",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
