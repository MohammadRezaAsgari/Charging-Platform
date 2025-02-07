from decimal import Decimal
from django.conf import settings
from django.urls import resolve, reverse
from rest_framework.test import APITestCase

from wallet.models import Currency, Invoice
from wallet.api.v1.views import InvoiceListAPIView, InvoiceByIDAPIView, WalletAPIView
from users.factories import UserFactory
from wallet.factories import InvoiceFactory


class TestInvoiceListAPIView(APITestCase):
    fixtures = ["wallet/fixtures/currencies.json"]

    def setUp(self):
        self.currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY_SIGN)
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("wallet:v1:invoice_list")

    def test_invoice_list_success(self):
        InvoiceFactory(user=self.user, amount=Decimal(100), currency=self.currency)
        InvoiceFactory(user=self.user, amount=Decimal(200), currency=self.currency)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("count"), 2)

    def test_create_invoice_success(self):
        data = {
            "amount": Decimal(100),
            "currency": self.user.wallet.currency,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get("success"), True)
        self.assertEqual(self.user.invoices.last().status, Invoice.StatusTypes.PENDING)

    def test_create_invoice_invalid_currency(self):
        data = {
            "amount": Decimal(100),
            "currency": "INVALID",
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("success"), False)
        self.assertIn("currency", response.json().get("error"))

    def test_resolve_url(self):
        resolver = resolve("/api/v1/wallet/invoices/")
        self.assertEqual(resolver.view_name, "wallet:v1:invoice_list")
        self.assertEqual(resolver.func.view_class, InvoiceListAPIView)


class TestInvoiceByIDAPIView(APITestCase):
    fixtures = ["wallet/fixtures/currencies.json"]

    def setUp(self):
        self.admin = UserFactory(is_superuser=True)
        self.client.force_authenticate(user=self.admin)
        self.user = UserFactory()
        self.currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY_SIGN)
        self.invoice = InvoiceFactory(
            user=self.user, amount=Decimal(100), currency=self.currency
        )
        self.url = reverse(
            "wallet:v1:invoice_detail", kwargs={"invoice_id": self.invoice.id}
        )

    def test_update_invoice_status_success(self):
        data = {"status": Invoice.StatusTypes.PAID}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 204)

    def test_update_invoice_not_found(self):
        url = reverse("wallet:v1:invoice_detail", kwargs={"invoice_id": 9999})
        response = self.client.patch(url, {"status": Invoice.StatusTypes.PAID})
        self.assertEqual(response.status_code, 404)

    def test_patch_not_pending_invoice_failed(self):
        self.invoice.status = Invoice.StatusTypes.PAID
        self.invoice.save()
        data = {"status": Invoice.StatusTypes.FAILED}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 406)

    def test_patch_as_non_admin_user_fail(self):
        self.client.force_authenticate(user=self.user)
        data = {"status": Invoice.StatusTypes.PAID}
        response = self.client.patch(self.url, data)
        self.assertEqual(response.status_code, 403)

    def test_resolve_url(self):
        resolver = resolve(f"/api/v1/wallet/invoices/{self.invoice.id}/")
        self.assertEqual(resolver.view_name, "wallet:v1:invoice_detail")
        self.assertEqual(resolver.func.view_class, InvoiceByIDAPIView)


class TestWalletAPIView(APITestCase):
    fixtures = ["wallet/fixtures/currencies.json"]

    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)
        self.url = reverse("wallet:v1:wallet")

    def test_retrieve_wallet_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get("success"), True)

    def test_resolve_url(self):
        resolver = resolve("/api/v1/wallet/balance/")
        self.assertEqual(resolver.view_name, "wallet:v1:wallet")
        self.assertEqual(resolver.func.view_class, WalletAPIView)
