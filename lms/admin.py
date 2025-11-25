from django.contrib import admin

from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    """
    Inline-представление уроков внутри курса в админке.
    Позволяет отображать и редактировать уроки прямо на странице
    редактирования курса, не переходя в отдельные формы.
    Особенности:
        - model: Lesson — уроки, связанные с курсом (FK course)
        - extra = 1 — выводит одну пустую строку для удобного добавления
          нового урока прямо из интерфейса курса.
    """

    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """
    Административный интерфейс модели Course.
    Отображает список курсов, а также включает LessonInline,
    что позволяет управлять уроками напрямую из формы курса.
    Настройки:
        - list_display: отображает id и название курса в списке
        - inlines: позволяет редактировать связанные уроки в рамках курса
    """

    list_display = ("id", "title")
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    """
    Административная конфигурация для модели Lesson.
    Обеспечивает удобный интерфейс для поиска, фильтрации
    и просмотра уроков.
    Настройки:
        - list_display: выводит id, название урока и привязанный курс
        - list_filter: добавляет фильтрацию по курсу
        - search_fields: включает поиск по названию урока и названию курса
          (course__title — поиск по связанному объекту)
    """

    list_display = ("id", "title", "course")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
