from rest_framework import viewsets, generics

from .models import User
from .serializers import UserSerializer, UserProfileSerializer


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