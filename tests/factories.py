import factory
from django.utils import timezone

from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from lms.models import Course, Lesson, Subscription
from users.models import Payment  # если модель Payment в users

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """
    Фабрика обычного пользователя.
    """

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    city = factory.Faker("city")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        pwd = extracted or "testpass123"
        self.set_password(pwd)
        if create:
            self.save()


class AdminFactory(UserFactory):
    """
    Фабрика админа (superuser).
    """

    is_staff = True
    is_superuser = True


class ModeratorGroupFactory(DjangoModelFactory):
    """
    Группа moderators.
    """

    class Meta:
        model = Group

    name = "moderators"


class ModeratorFactory(UserFactory):
    """
    Пользователь, состоящий в группе moderators.
    """

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        group, _ = Group.objects.get_or_create(name="moderators")
        self.groups.add(group)


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Sequence(lambda n: f"Курс {n}")
    description = factory.Faker("sentence")
    owner = factory.SubFactory(UserFactory)


class LessonFactory(DjangoModelFactory):
    class Meta:
        model = Lesson

    course = factory.SubFactory(CourseFactory)
    title = factory.Sequence(lambda n: f"Урок {n}")
    description = factory.Faker("sentence")
    video_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    owner = factory.SubFactory(UserFactory)


class SubscriptionFactory(DjangoModelFactory):
    class Meta:
        model = Subscription

    user = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)


class PaymentFactory(DjangoModelFactory):
    class Meta:
        model = Payment

    user = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
    lesson = None
    amount = 1000
    paid_at = factory.LazyFunction(timezone.now)

    @factory.lazy_attribute
    def payment_method(self):
        """
        Берём первое значение из choices поля payment_method модели Payment.
        """
        field = Payment._meta.get_field("payment_method")
        choices = getattr(field, "choices", None)
        return choices[0][0] if choices else "cash"
