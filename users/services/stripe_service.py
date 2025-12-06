from decimal import Decimal

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_stripe_product(name: str) -> stripe.Product:
    """
    Создание продукта в Stripe.
    :param name: Название продукта (например, имя курса или урока)
    :return: объект stripe.Product
    """
    return stripe.Product.create(name=name)


def create_stripe_price(
    *,
    product_id: str,
    amount: float | Decimal,
    currency: str = "usd",
) -> stripe.Price:
    """
    Создание цены в Stripe.
    Важно: Stripe ждёт цену в копейках/центах.
    amount: 1000.00 (руб) -> 100000 (копеек), если бы валюта была rub.
    Сейчас по умолчанию используем usd и cents.
    :param product_id: stripe.Product.id
    :param amount: сумма в единицах валюты (например, 10.00 долларов)
    :param currency: код валюты (usd, eur, etc.)
    :return: объект stripe.Price
    """
    unit_amount = int(Decimal(str(amount)) * 100)

    return stripe.Price.create(
        product=product_id,
        unit_amount=unit_amount,
        currency=currency,
    )


def create_checkout_session(
    *,
    price_id: str,
    success_url: str,
    cancel_url: str,
) -> stripe.checkout.Session:
    """
    Создание Checkout Session в Stripe для получения ссылки на оплату.
    :param price_id: stripe.Price.id
    :param success_url: URL, на который пользователь попадёт после успешной оплаты
    :param cancel_url: URL при отмене оплаты
    :return: объект stripe.checkout.Session
    """
    return stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        success_url=success_url,
        cancel_url=cancel_url,
    )


def retrieve_checkout_session(session_id: str) -> stripe.checkout.Session:
    """
    Получить данные сессии по id (опционально, для проверки статуса).
    :param session_id: stripe.CheckoutSession.id
    """
    return stripe.checkout.Session.retrieve(session_id)
