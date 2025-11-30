from rest_framework import serializers
from .validators import validate_only_youtube

from .models import Course, Lesson, Subscription


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Lesson.
    Используется для создания, обновления и отображения уроков.
    Предоставляет плоское представление данных, соответствующее
    структуре модели.
    Поля:
        - id: первичный ключ (только для чтения)
        - course: ID курса, к которому относится урок
        - title: название урока
        - description: описание урока
        - preview: изображение-превью (опционально)
        - video_link: ссылка на видеоурок
    Применяется в CRUD-операциях для уроков:
    - ListCreateAPIView (список и создание)
    - RetrieveUpdateDestroyAPIView (детальный просмотр и редактирование)
     Важное ограничение:
    - поле video_link допускает только ссылки на YouTube (youtube.com / youtu.be).
    """

    video_link = serializers.URLField(
        validators=[validate_only_youtube],
        help_text="Ссылка на YouTube-видео (youtube.com или youtu.be).",
    )

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "title",
            "description",
            "preview",
            "video_link",
            "owner",
        ]
        read_only_fields = ["id", "owner"]


class CourseSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели Course.
    Помимо основных полей курса, включает вложенный список уроков,
    доступный только для чтения. Это позволяет при получении деталей
    курса отображать связанные уроки без необходимости выполнять
    отдельный запрос.
    Поля:
        - id: первичный ключ (только для чтения)
        - title: название курса
        - preview: изображение-превью курса
        - description: текстовое описание курса
        - lessons: вложенный список уроков, связанных с данным курсом
                   (чтение-only, сериализуется через LessonSerializer)
    Использование вложенных сериализаторов делает ответ более
    информативным и удобным для фронтенда, который получает структуру
    курса вместе с его уроками одним запросом.
    """

    # вложенные уроки только для чтения (GET)
    lessons = LessonSerializer(many=True, read_only=True)

    # количество уроков в курсе
    lessons_count = serializers.SerializerMethodField()

    # признак подписки текущего пользователя
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "lessons",
            "lessons_count",
            "owner",
            "is_subscribed",
        ]
        read_only_fields = ["id", "owner", "lessons_count", "is_subscribed"]

    def get_lessons_count(self, obj) -> int:
        """
        Возвращает количество уроков, связанных с данным курсом.
        Используется SerializerMethodField, чтобы явно контролировать
        способ вычисления значения.
        """
        return obj.lessons.count()

    def get_is_subscribed(self, obj) -> bool:
        """
        Возвращает True, если текущий пользователь подписан на курс.
        Для неавторизованных — всегда False.
        """
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False

        user = request.user
        return obj.subscriptions.filter(user=user).exists()
