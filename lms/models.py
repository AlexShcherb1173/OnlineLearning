from django.db import models
from django.conf import settings


class Course(models.Model):
    """
    Модель Course (Курс).
    Представляет учебный курс в системе онлайн-обучения.

    Поля:
        title (CharField):
            Название курса. Обязательное поле, используется в административных
            панелях и отображениях.
        preview (ImageField):
            Изображение-превью курса. Необязательное поле.
            Загружается в директорию "courses/previews/".
        description (TextField):
            Текстовое описание курса. Может быть пустым, используется для
            отображения структуры курса на фронтенде.
        owner (ForeignKey):
            Владелец курса (пользователь системы).
        last_notification_at (DateTimeField):
            Время последней рассылки уведомлений об обновлении курса.
            Используется для ограничения частоты уведомлений (не чаще одного
            раза в N часов, сейчас — 4 часа).
        updated_at (DateTimeField):
            Время последнего изменения курса (auto_now=True).
            Может использоваться для аналитики и отображения.
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Название курса",
    )
    preview = models.ImageField(
        upload_to="courses/previews/",
        blank=True,
        null=True,
        verbose_name="Превью курса",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание курса",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец курса",
        null=True,
        blank=True,  # чтобы не падали старые записи
    )

    last_notification_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="время последней рассылки об обновлении",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="время последнего изменения курса",
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["title"]


class Lesson(models.Model):
    """
    Модель Lesson (Урок).
    Представляет отдельный учебный урок, который относится
    к определённому курсу.

    Поля:
        course (ForeignKey):
            Внешний ключ на Course. Один курс может содержать много уроков.
            related_name="lessons" позволяет обращаться к урокам как course.lessons.
            При удалении курса связанные уроки удаляются (CASCADE).
        title (CharField):
            Название урока. Обязательное поле.
        description (TextField):
            Описание урока. Может быть пустым.
        preview (ImageField):
            Изображение-превью урока. Необязательное.
            Загружается в "lessons/previews/".
        video_link (URLField):
            URL-ссылка на видео урока.
        owner (ForeignKey):
            Владелец урока (преподаватель / автор).
    Особенности:
        - __str__ возвращает строку вида:
          "<Название курса>: <Название урока>".
        - ordering — сортировка по курсу и ID (естественный порядок уроков).
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Название урока",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание урока",
    )
    preview = models.ImageField(
        upload_to="lessons/previews/",
        blank=True,
        null=True,
        verbose_name="Превью урока",
    )
    video_link = models.URLField(
        verbose_name="Ссылка на видео",
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец урока",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.course.title}: {self.title}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["course", "id"]


class Subscription(models.Model):
    """
    Подписка пользователя на обновления курса.

    Один пользователь может быть подписан на один курс
    не более одного раза (unique_together).

    Используется для:
    - асинхронной рассылки писем об обновлении материалов курса;
    - фильтрации получателей при отправке уведомлений.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подписки",
    )

    class Meta:
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курсы"
        unique_together = ("user", "course")

    def __str__(self) -> str:
        # Защита от случаев, когда у пользователя нет email
        email = getattr(self.user, "email", "") or self.user.pk
        return f"{email} → {self.course.title}"
