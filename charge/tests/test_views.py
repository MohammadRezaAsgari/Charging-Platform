from decimal import Decimal
from django.conf import settings
from django.urls import resolve, reverse
from rest_framework.test import APITestCase

from charge.api.v1.views import ChargingListAPIView
from charge.factories import ChargingFactory
from users.factories import UserFactory
from utils.api.error_objects import ErrorObject
from wallet.models import Currency


class TestChargingListAPIView(APITestCase):
    fixtures = ["wallet/fixtures/currencies.json"]

    def setUp(self):
        self.currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY_SIGN)
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("charge:v1:charging_list")

    def test_charging_list_success(self):
        ChargingFactory(
            user=self.user,
            phone="+989123456789",
            amount=Decimal(100),
            currency=self.currency,
        )
        ChargingFactory(
            user=self.user,
            phone="+989123456789",
            amount=Decimal(100),
            currency=self.currency,
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 2)

    def test_create_charging_success(self):
        self.user.wallet.balance = Decimal(50)
        self.user.wallet.save()
        data = {
            "phone": "+989123456789",
            "amount": Decimal(50),
            "currency": self.user.wallet.currency,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get("success"), True)
        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, Decimal(0))

    def test_create_charging_invalid_currency(self):
        self.user.wallet.balance = Decimal(50)
        self.user.wallet.save()
        data = {
            "phone": "+989123456789",
            "amount": Decimal(50),
            "currency": "INVALID",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("success"), False)
        self.assertIn("currency", response.json().get("error"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, Decimal(50))

    def test_create_charging_insufficient_balance(self):
        self.user.wallet.balance = Decimal(0)
        self.user.wallet.save()
        data = {
            "phone": "+989123456789",
            "amount": Decimal(50),
            "currency": self.user.wallet.currency,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response.json().get("success"), False)
        self.assertEqual(
            response.json().get("error")["code"], ErrorObject.NOT_ENOUGH_BALANCE["code"]
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, Decimal(0))

    def test_resolve_url(self):
        resolver = resolve("/api/v1/charge/chargings/")
        self.assertEqual(resolver.view_name, "charge:v1:charging_list")
        self.assertEqual(resolver.func.view_class, ChargingListAPIView)
