from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from lms.models import Course, Lesson, Subscription
from tests.factories import (
    AdminFactory,
    UserFactory,
    ModeratorFactory,
    CourseFactory,
    LessonFactory,
    SubscriptionFactory,
)


class LessonCRUDTests(APITestCase):
    """
    Тесты CRUD для уроков:
    - доступ к списку (пагинация)
    - создание (только админ)
    - просмотр (любой аутентифицированный)
    - обновление/удаление (права по ролям)
    """

    def setUp(self):
        self.client = APIClient()

        self.admin = AdminFactory(email="admin@example.com")
        self.user = UserFactory(email="user@example.com")

        self.course = CourseFactory(owner=self.admin)
        self.lesson = LessonFactory(course=self.course, owner=self.admin)

    def test_lesson_list_requires_auth(self):
        url = reverse("lesson-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_lesson_list_authenticated_paginated(self):
        url = reverse("lesson-list-create")
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertIn("count", response.data)

    def test_lesson_create_admin_ok(self):
        """
        Администратор может создать урок.
        """
        url = reverse("lesson-list-create")
        self.client.force_authenticate(self.admin)

        data = {
            "course": self.course.id,
            "title": "Новый урок",
            "description": "Описание",
            "video_link": "https://youtu.be/dQw4w9WgXcQ",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)
        created = Lesson.objects.get(id=response.data["id"])
        self.assertEqual(created.owner, self.admin)

    def test_lesson_create_non_admin_forbidden(self):
        """
        Обычный пользователь НЕ может создавать урок.
        """
        url = reverse("lesson-list-create")
        self.client.force_authenticate(self.user)

        data = {
            "course": self.course.id,
            "title": "Новый урок",
            "description": "Описание",
            "video_link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_retrieve_any_authenticated_ok(self):
        """
        Любой аутентифицированный пользователь может просматривать урок.
        """
        url = reverse("lesson-detail", args=[self.lesson.id])
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.lesson.id)

    def test_lesson_update_admin_ok(self):
        """
        Владелец (админ) может обновить урок.
        """
        url = reverse("lesson-detail", args=[self.lesson.id])
        self.client.force_authenticate(self.admin)

        data = {
            "course": self.course.id,
            "title": "Обновленный урок",
            "description": "Новое описание",
            "video_link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновленный урок")

    def test_lesson_update_foreign_user_forbidden(self):
        """
        Не-владелец (и не модератор/админ) не может обновить урок.
        """
        url = reverse("lesson-detail", args=[self.lesson.id])
        self.client.force_authenticate(self.user)

        data = {
            "course": self.course.id,
            "title": "Попытка обновления",
            "description": "Описание",
            "video_link": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }

        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_admin_only(self):
        """
        Удалять урок может только админ.
        """
        url = reverse("lesson-detail", args=[self.lesson.id])

        # обычный пользователь
        self.client.force_authenticate(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # админ
        self.client.force_authenticate(self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())


class SubscriptionTests(APITestCase):
    """
    Тесты функционала подписки на курс:
    - требование авторизации
    - создание/удаление подписки (toggle)
    - отражение флага is_subscribed в детальном курсе.
    """

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory(email="subuser@example.com")
        # Курс делаем владельцем именно этого пользователя,
        # чтобы он попадал в queryset и не давал 404
        self.course = CourseFactory(owner=self.user)

    def test_subscription_requires_auth(self):
        url = reverse("course-subscribe")
        response = self.client.post(url, {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscribe_create(self):
        """
        Если подписки нет — создаётся.
        """
        url = reverse("course-subscribe")
        self.client.force_authenticate(self.user)

        response = self.client.post(url, {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_toggle_delete(self):
        """
        Повторный POST удаляет существующую подписку.
        """
        SubscriptionFactory(user=self.user, course=self.course)

        url = reverse("course-subscribe")
        self.client.force_authenticate(self.user)

        response = self.client.post(url, {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_course_detail_contains_is_subscribed(self):
        """
        Поле is_subscribed в CourseSerializer зависит от подписки текущего пользователя.
        """
        url = reverse("course-detail", args=[self.course.id])

        # без подписки
        self.client.force_authenticate(self.user)
        resp1 = self.client.get(url)
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        self.assertIn("is_subscribed", resp1.data)
        self.assertFalse(resp1.data["is_subscribed"])

        # с подпиской
        SubscriptionFactory(user=self.user, course=self.course)
        resp2 = self.client.get(url)
        self.assertTrue(resp2.data["is_subscribed"])


class CourseViewSetTests(APITestCase):
    """
    Тесты CRUD для CourseViewSet с учётом ролей:
    - обычный пользователь видит/редактирует только свои курсы
    - модератор видит и редактирует любые, но не создаёт/не удаляет
    - админ может всё.
    """

    def setUp(self):
        self.client = APIClient()

        self.admin = AdminFactory(email="admin@example.com")
        self.moderator = ModeratorFactory(email="moderator@example.com")
        self.user1 = UserFactory(email="user1@example.com")
        self.user2 = UserFactory(email="user2@example.com")

        self.course1 = CourseFactory(owner=self.user1, title="Курс user1")
        self.course2 = CourseFactory(owner=self.user2, title="Курс user2")

    def test_course_list_anonymous_401(self):
        url = reverse("course-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_course_list_user_sees_only_own(self):
        url = reverse("course-list")
        self.client.force_authenticate(self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ids = [c["id"] for c in resp.data["results"]]
        self.assertIn(self.course1.id, ids)
        self.assertNotIn(self.course2.id, ids)

    def test_course_list_moderator_sees_all(self):
        url = reverse("course-list")
        self.client.force_authenticate(self.moderator)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [c["id"] for c in resp.data["results"]]
        self.assertIn(self.course1.id, ids)
        self.assertIn(self.course2.id, ids)

    def test_course_list_admin_sees_all(self):
        url = reverse("course-list")
        self.client.force_authenticate(self.admin)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [c["id"] for c in resp.data["results"]]
        self.assertIn(self.course1.id, ids)
        self.assertIn(self.course2.id, ids)

    def test_course_create_admin_ok(self):
        url = reverse("course-list")
        self.client.force_authenticate(self.admin)
        data = {"title": "Новый курс", "description": "Описание"}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Course.objects.filter(id=resp.data["id"], owner=self.admin).exists()
        )

    def test_course_create_moderator_forbidden(self):
        url = reverse("course-list")
        self.client.force_authenticate(self.moderator)
        data = {"title": "Курс модератора", "description": "Описание"}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_create_user_forbidden(self):
        url = reverse("course-list")
        self.client.force_authenticate(self.user1)
        data = {"title": "Курс пользователя", "description": "Описание"}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_update_owner_ok(self):
        url = reverse("course-detail", args=[self.course1.id])
        self.client.force_authenticate(self.user1)
        data = {"title": "Обновлённый курс", "description": "upd"}
        resp = self.client.put(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.course1.refresh_from_db()
        self.assertEqual(self.course1.title, "Обновлённый курс")

    def test_course_update_foreign_user_forbidden(self):
        url = reverse("course-detail", args=[self.course2.id])
        self.client.force_authenticate(self.user1)
        data = {"title": "Хочу изменить чужой курс", "description": "hack"}
        resp = self.client.put(url, data, format="json")
        # в зависимости от реализации: либо 403 (object-level perms), либо 404 (нет в queryset)
        self.assertIn(
            resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND)
        )

    def test_course_update_moderator_ok(self):
        url = reverse("course-detail", args=[self.course2.id])
        self.client.force_authenticate(self.moderator)
        data = {"title": "Модератор меняет курс", "description": "mod"}
        resp = self.client.put(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.course2.refresh_from_db()
        self.assertEqual(self.course2.title, "Модератор меняет курс")

    def test_course_delete_admin_ok(self):
        url = reverse("course-detail", args=[self.course1.id])
        self.client.force_authenticate(self.admin)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(id=self.course1.id).exists())

    def test_course_delete_moderator_forbidden(self):
        url = reverse("course-detail", args=[self.course2.id])
        self.client.force_authenticate(self.moderator)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_course_delete_owner_forbidden(self):
        url = reverse("course-detail", args=[self.course1.id])
        self.client.force_authenticate(self.user1)
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
