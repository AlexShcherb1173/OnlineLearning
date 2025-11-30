from urllib.parse import urlparse

from rest_framework import serializers


def validate_only_youtube(value: str) -> str:
    """
    Валидатор для проверки того, что ссылка указывает только на YouTube.
    Разрешённые домены:
      - youtube.com
      - www.youtube.com
      - youtu.be
      - www.youtu.be
    Любые другие домены считаются сторонними ресурсами
    и запрещены для использования в учебных материалах.
    """
    parsed = urlparse(value)
    domain = parsed.netloc.lower()

    allowed_domains = {
        "youtube.com",
        "www.youtube.com",
        "youtu.be",
        "www.youtu.be",
    }

    if domain not in allowed_domains:
        raise serializers.ValidationError(
            "Разрешены только ссылки на YouTube (youtube.com или youtu.be)."
        )

    return value
