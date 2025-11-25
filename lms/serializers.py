from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
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
    # вложенные уроки только для чтения (GET)
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "preview",
            "description",
            "lessons",
        ]
        read_only_fields = ["id"]