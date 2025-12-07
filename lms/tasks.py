import logging
from typing import List

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Course, Lesson, Subscription

logger = logging.getLogger(__name__)


@shared_task
def send_course_update_notifications(course_id: int, lesson_id: int) -> int:
    """
    Асинхронная задача для рассылки писем подписчикам курса
    об обновлении материалов (конкретного урока).
    - Берёт курс и урок по ID.
    - Находит всех подписчиков (Subscription) с заполненным email.
    - Отправляет одно письмо с копией всем подписчикам.
    - Возвращает количество адресатов, которым попытались отправить письмо.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        logger.warning("Course %s does not exist, skip notification", course_id)
        return 0

    try:
        lesson = Lesson.objects.get(pk=lesson_id)
    except Lesson.DoesNotExist:
        logger.warning("Lesson %s does not exist, skip notification", lesson_id)
        return 0

    # Активные подписки на курс
    subscriptions = Subscription.objects.filter(course=course).select_related("user")

    recipients: List[str] = []
    for sub in subscriptions:
        user = sub.user
        email = getattr(user, "email", None)
        if email:
            recipients.append(email)

    if not recipients:
        logger.info(
            "No subscribers with email for course %s, notification skipped",
            course.id,
        )
        return 0

    subject = f"Обновление курса «{course.title}»"
    message = (
        f"В курсе «{course.title}» обновлён урок «{lesson.title}».\n\n"
        f"Зайдите в личный кабинет, чтобы ознакомиться с новыми материалами."
    )

    from_email = (
        getattr(settings, "DEFAULT_FROM_EMAIL", None)
        or getattr(settings, "EMAIL_HOST_USER", None)
        or "noreply@example.com"
    )

    sent_count = send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=recipients,
        fail_silently=False,
    )

    logger.info(
        "Sent course update notifications: course=%s, lesson=%s, recipients=%s",
        course.id,
        lesson.id,
        len(recipients),
    )

    # Обновлять last_notification_at в контроллере после решения о рассылке,
    # чтобы логика "не чаще, чем раз в 4 часа" была в одном месте.
    return sent_count


@shared_task
def example_periodic_task():
    logger.info("example_periodic_task tick")
    return "OK"
