import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task
def deactivate_inactive_users() -> int:
    """
    Деактивирует обычных пользователей, которые не заходили более 30 дней.
    Правила:
      - is_active=True
      - is_staff=False
      - is_superuser=False
      - last_login < now - 30 дней
        ИЛИ last_login is NULL и date_joined < now - 30 дней
    Админов и суперпользователей не трогаем.
    """
    now = timezone.now()
    threshold = now - timedelta(days=30)

    qs = User.objects.filter(
        is_active=True,
        is_staff=False,
        is_superuser=False,
    ).filter(
        Q(last_login__lt=threshold)
        | Q(last_login__isnull=True, date_joined__lt=threshold)
    )

    count = qs.update(is_active=False)

    logger.info(
        "deactivate_inactive_users: deactivated %s users (threshold=%s)",
        count,
        threshold.isoformat(),
    )
    return count
