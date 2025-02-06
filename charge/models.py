from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField


class Charging(TimeStampedModel):
    phone = PhoneNumberField()
    user = models.ForeignKey(
        "users.User",
        related_name="chargings",
        on_delete=models.PROTECT,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=14,
    )
    currency = models.ForeignKey(
        "wallet.Currency",
        related_name="chargings",
        on_delete=models.PROTECT,
        default=settings.DEFAULT_CURRENCY_SIGN,
    )

    def __str__(self):
        return f"{self.phone}-{self.user.username}"
