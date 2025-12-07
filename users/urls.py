from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    UserViewSet,
    UserProfileRetrieveUpdateAPIView,
    PaymentListAPIView,
    StripeCheckoutCreateAPIView,
    StripePaymentStatusAPIView,
)

"""
    URL-конфигурация приложения users.
    1. ViewSet пользователей (UserViewSet):
    2. ViewSet платежей (PaymentViewSet):
       - CRUD по /api/users/payments/
    3. Stripe API endpoints:
      - POST /api/users/payments/stripe-checkout/
      - GET  /api/users/payments/stripe-status/<id>/
    4. Профиль пользователя:
      - GET/PUT/PATCH /api/users/profiles/<id>/
"""

# ----------------------
# ViewSets
# ----------------------
router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")


# ----------------------
# Остальные эндпоинты
# ----------------------
urlpatterns = [
    # Профиль пользователя
    path(
        "profiles/<int:pk>/",
        UserProfileRetrieveUpdateAPIView.as_view(),
        name="user-profile-detail",
    ),
    # Полный список платежей (не ViewSet)
    path(
        "payments/all/",
        PaymentListAPIView.as_view(),
        name="payment-list-all",
    ),
    # Stripe Checkout
    path(
        "payments/stripe-checkout/",
        StripeCheckoutCreateAPIView.as_view(),
        name="stripe-checkout",
    ),
    path(
        "payments/stripe-status/<int:pk>/",
        StripePaymentStatusAPIView.as_view(),
        name="stripe-status",
    ),
]

# Добавляем маршруты ViewSet
urlpatterns += router.urls
