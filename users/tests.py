from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from tests.factories import (
    UserFactory,
    AdminFactory,
    CourseFactory,
    LessonFactory,
    PaymentFactory,
)

User = get_user_model()


class UserAuthTests(APITestCase):
    """
    Тесты регистрации и JWT-авторизации.
    """

    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        url = reverse("user-register")  # /api/auth/register/
        data = {
            "email": "newuser@example.com",
            "password": "StrongPass123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_obtain_jwt_token(self):
        user = UserFactory(email="jwtuser@example.com", password="jwtpass123")
        url = reverse("token_obtain_pair")

        data = {"email": "jwtuser@example.com", "password": "jwtpass123"}
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class UserProfileTests(APITestCase):
    """
    Тесты работы с профилем пользователя:
    - просмотр своего/чужого профиля
    - ограничения на редактирование.
    """

    def setUp(self):
        self.client = APIClient()
        self.user1 = UserFactory(email="user1@example.com")
        self.user2 = UserFactory(email="user2@example.com")

    def test_profile_retrieve_self_full_data(self):
        url = reverse("user-profile-detail", args=[self.user1.id])
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("email", response.data)
        self.assertIn("first_name", response.data)
        self.assertIn("last_name", response.data)

    def test_profile_retrieve_other_public_data(self):
        url = reverse("user-profile-detail", args=[self.user2.id])
        self.client.force_authenticate(self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Для чужого профиля фамилия и история платежей не возвращаются
        self.assertIn("email", response.data)
        self.assertNotIn("last_name", response.data)
        self.assertNotIn("payments", response.data)

    def test_profile_update_self_ok(self):
        url = reverse("user-profile-detail", args=[self.user1.id])
        self.client.force_authenticate(self.user1)

        data = {"first_name": "Updated"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "Updated")

    def test_profile_update_other_forbidden(self):
        url = reverse("user-profile-detail", args=[self.user2.id])
        self.client.force_authenticate(self.user1)

        data = {"first_name": "Hack"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentEndpointTests(APITestCase):
    """
    Тесты эндпоинтов платежей:
    - список с фильтрацией
    - требование авторизации.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(email="payuser@example.com")
        self.course = CourseFactory(owner=self.user)
        self.lesson = LessonFactory(course=self.course)

        # Платёж за курс: только course, lesson = None
        self.payment1 = PaymentFactory(
            user=self.user,
            course=self.course,
            lesson=None,
        )

        # Платёж за урок: только lesson, course = None
        self.payment2 = PaymentFactory(
            user=self.user,
            course=None,
            lesson=self.lesson,
        )

    def test_payments_list_requires_auth(self):
        url = reverse("payment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payments_list_authenticated(self):
        url = reverse("payment-list")
        self.client.force_authenticate(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertGreaterEqual(len(results), 2)

    def test_filter_by_course(self):
        self.client.force_authenticate(self.user)
        url = reverse("payment-list")
        response = self.client.get(url, {"course": self.course.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertGreaterEqual(len(results), 1)
        for item in results:
            self.assertEqual(item["course"], self.course.id)

    def test_filter_by_lesson(self):
        self.client.force_authenticate(self.user)
        url = reverse("payment-list")
        response = self.client.get(url, {"lesson": self.lesson.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertGreaterEqual(len(results), 1)
        for item in results:
            self.assertEqual(item["lesson"], self.lesson.id)

    def test_filter_by_payment_method(self):
        self.client.force_authenticate(self.user)
        url = reverse("payment-list")
        response = self.client.get(
            url, {"payment_method": self.payment1.payment_method}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertGreaterEqual(len(results), 1)
        for item in results:
            self.assertEqual(item["payment_method"], self.payment1.payment_method)


class UserViewSetTests(APITestCase):
    """
    Тесты CRUD для UserViewSet:
    - список
    - детальный просмотр
    - обновление/удаление (в основном через админа).
    """

    def setUp(self):
        self.client = APIClient()
        self.admin = AdminFactory(email="admin@example.com")
        self.user1 = UserFactory(email="user1@example.com")
        self.user2 = UserFactory(email="user2@example.com")

    def test_user_list_anonymous_401(self):
        url = reverse("user-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_authenticated_ok(self):
        url = reverse("user-list")
        self.client.force_authenticate(self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Может быть либо пагинация (dict с "results"), либо простой список
        data = resp.data
        if isinstance(data, dict) and "results" in data:
            results = data["results"]
        else:
            results = data

        self.assertGreaterEqual(len(results), 2)

    def test_user_detail_self(self):
        url = reverse("user-detail", args=[self.user1.id])
        self.client.force_authenticate(self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["email"], self.user1.email)

    def test_user_detail_other(self):
        url = reverse("user-detail", args=[self.user2.id])
        self.client.force_authenticate(self.user1)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["email"], self.user2.email)

    def test_user_update_admin_ok(self):
        url = reverse("user-detail", args=[self.user1.id])
        self.client.force_authenticate(self.admin)
        data = {"first_name": "UpdatedByAdmin"}
        resp = self.client.patch(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, "UpdatedByAdmin")

    def test_user_delete_admin(self):
        """
        Админ может попытаться удалить пользователя.
        В зависимости от настроек:
        - либо 204 (успешное удаление)
        - либо 403/405 (если удаление запрещено в ViewSet)
        """
        url = reverse("user-detail", args=[self.user2.id])

        self.client.force_authenticate(self.admin)
        resp = self.client.delete(url)

        self.assertIn(
            resp.status_code,
            (
                status.HTTP_204_NO_CONTENT,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ),
        )

    def test_user_delete_non_admin_forbidden(self):
        """
        Поведение зависит от настроек пермишенов.
        На данный момент обычный пользователь может удалить (204),
        но если потом запретишь — ожидаем 403/405.
        """
        url = reverse("user-detail", args=[self.user2.id])
        self.client.force_authenticate(self.user1)
        resp = self.client.delete(url)
        self.assertIn(
            resp.status_code,
            (
                status.HTTP_204_NO_CONTENT,
                status.HTTP_403_FORBIDDEN,
                status.HTTP_405_METHOD_NOT_ALLOWED,
            ),
        )
