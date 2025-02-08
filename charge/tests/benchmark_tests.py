import pytest
from decimal import Decimal
from django.urls import reverse
from charge.factories import ChargingFactory
from users.factories import UserFactory
from wallet.models import Currency


@pytest.mark.django_db
@pytest.fixture
def setup_charging_data():
    currency = Currency.objects.create(
        code="USD",
        number="840",
        name="US Dollar",
        symbol="$",
        major_unit_name="dollar",
        minor_unit={},
    )
    user = UserFactory()
    return user, currency


@pytest.mark.django_db
def test_charging_list_success(client, setup_charging_data, benchmark):
    user, currency = setup_charging_data
    client.force_login(user)
    ChargingFactory(
        user=user, phone="+989123456789", amount=Decimal(100), currency=currency
    )
    ChargingFactory(
        user=user, phone="+989123456789", amount=Decimal(100), currency=currency
    )

    url = reverse("charge:v1:charging_list")
    response = benchmark(lambda: client.get(url))

    assert response.status_code == 200
    assert response.json().get("count") == 2
