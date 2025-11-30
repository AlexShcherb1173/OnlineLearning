import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


User = get_user_model()


class Command(BaseCommand):
    help = "Создаёт дефолтного суперпользователя, если он ещё не существует."

    def add_arguments(self, parser):
        """
        Дополнительные аргументы команды:
        - --email
        - --password
        Если их не указать, возьмём значения из переменных окружения
        DJANGO_DEFAULT_ADMIN_EMAIL и DJANGO_DEFAULT_ADMIN_PASSWORD
        или дефолтные значения.
        """
        parser.add_argument(
            "--email",
            type=str,
            default=os.getenv("DJANGO_DEFAULT_ADMIN_EMAIL", "admin@example.com"),
            help="Email суперпользователя (по умолчанию admin@example.com)",
        )
        parser.add_argument(
            "--password",
            type=str,
            default=os.getenv("DJANGO_DEFAULT_ADMIN_PASSWORD", "admin12345"),
            help="Пароль суперпользователя (по умолчанию admin12345)",
        )

    def handle(self, *args, **options):
        email = options["email"]
        password = options["password"]

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Пользователь с email {email} уже существует. Ничего не делаем."
                )
            )
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(
            self.style.SUCCESS(
                f"Суперпользователь создан: {email} (пароль: {password})"
            )
        )
