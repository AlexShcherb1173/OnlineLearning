from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission

User = get_user_model()


class IsModerator(BasePermission):
    """
    Разрешение, проверяющее, что пользователь входит в группу 'moderators'.
    """

    message = "Доступ разрешён только модераторам."

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and user.groups.filter(name="moderators").exists()
        )


class IsModeratorOrAdmin(BasePermission):
    """
    Разрешение для модераторов и администраторов.
    Используется там, где нужно разрешить редактирование:
    - модератору (группа 'moderators'),
    - администратору (is_staff / is_superuser).
    """

    message = "Доступ разрешён только модераторам или администраторам."

    def has_permission(self, request, view) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        is_moderator = user.groups.filter(name="moderators").exists()
        is_admin = user.is_staff or user.is_superuser
        return is_moderator or is_admin


class IsOwner(BasePermission):
    """
    Разрешение на уровне объекта: пользователь является владельцем.

    Для удобства:
    - модераторов и админов тоже считаем "имеющими доступ" (они и так
      проверяются отдельными пермишенами, но это защищает от лишних падений).
    """

    message = "Доступ разрешён только владельцу объекта или модератору/администратору."

    def has_permission(self, request, view) -> bool:
        # На уровне запроса просто пускаем всех аутентифицированных,
        # детальная проверка — в has_object_permission.
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj) -> bool:
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # если у объекта нет поля owner — не даём доступ
        owner = getattr(obj, "owner", None)

        is_moderator = user.groups.filter(name="moderators").exists()
        is_admin = user.is_staff or user.is_superuser

        return is_admin or is_moderator or (owner == user)


class IsProfileOwner(BasePermission):
    """
    Разрешает редактировать профиль только его владельцу.
    """

    message = "Вы можете редактировать только свой профиль."

    def has_object_permission(self, request, view, obj):
        # Только владелец может изменять данные
        if request.method in ("PUT", "PATCH"):
            return obj == request.user
        return True
