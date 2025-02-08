import pytest
from decimal import Decimal
from django.urls import reverse
from wallet.factories import InvoiceFactory
from users.factories import UserFactory
from wallet.models import Currency, Invoice


@pytest.mark.django_db
@pytest.fixture
def setup_currency():
    Currency.objects.create(
        code="USD",
        number="840",
        name="US Dollar",
        symbol="$",
        major_unit_name="dollar",
        minor_unit={},
    )


@pytest.mark.django_db
def test_invoice_list_performance(client, setup_currency, benchmark):
    user = UserFactory()
    client.force_login(user)
    url = reverse("wallet:v1:invoice_list")

    InvoiceFactory.create_batch(100, user=user, amount=Decimal(100))
    response = benchmark(lambda: client.get(url))
    assert response.status_code == 200
    assert response.json().get("count") == 100


@pytest.mark.django_db
def test_create_invoice_performance(client, setup_currency, benchmark):
    user = UserFactory()
    client.force_login(user)
    url = reverse("wallet:v1:invoice_list")

    data = {
        "amount": Decimal(100),
        "currency": user.wallet.currency,
    }

    response = benchmark(lambda: client.post(url, data))
    assert response.status_code == 201
    assert response.json().get("success") is True
    assert user.invoices.last().status == Invoice.StatusTypes.PENDING
