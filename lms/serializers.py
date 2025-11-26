from rest_framework import serializers

from .models import Course, Lesson


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
    """

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "title",
            "description",
            "preview",
            "video_link",
        ]
        read_only_fields = ["id"]


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

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "lessons",
            "lessons_count",
        ]
        read_only_fields = ["id"]

    def get_lessons_count(self, obj) -> int:
        """
        Возвращает количество уроков, связанных с данным курсом.
        Используется SerializerMethodField, чтобы явно контролировать
        способ вычисления значения.
        """
        return obj.lessons.count()
