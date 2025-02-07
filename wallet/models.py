from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import IntegrityError, models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from utils.helpers import create_random_str
from utils.loggers import stdout_logger

User = get_user_model()


class Currency(models.Model):
    code = models.CharField(
        _("code ISO 4217"),
        max_length=3,
        primary_key=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{3}$",
                message=_("code must be ISO 4217"),
            ),
        ],
    )
    number = models.CharField(
        _("code ISO 4217 numeric"),
        max_length=3,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{3}$",
                message=_("code must be ISO 4217 numeric"),
            ),
        ],
    )
    name = models.CharField(max_length=32)
    symbol = models.CharField(blank=True, max_length=16)
    major_unit_name = models.CharField(max_length=32)
    minor_unit = models.JSONField()

    class Meta:
        ordering = ("code",)
        verbose_name = _("currency")
        verbose_name_plural = _("currencies")

    def __str__(self):
        return self.code


class Wallet(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet",
    )
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="wallets",
        default=settings.DEFAULT_CURRENCY_SIGN,
    )
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    def __str__(self):
        return f"{self.user} - {self.currency}"

    def save(self, *args, **kwargs):
        if not self.currency_id:
            self.currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY_SIGN)
        super().save(*args, **kwargs)

    def has_enough_credit(self, amount):
        if amount > self.balance:
            return False
        return True


class Invoice(TimeStampedModel):
    class StatusTypes(models.IntegerChoices):
        PENDING = 1
        PAID = 2
        FAILED = 3

    code = models.CharField(unique=True, max_length=255, null=False, blank=True)
    user = models.ForeignKey(
        "users.User",
        related_name="invoices",
        on_delete=models.PROTECT,
    )
    amount = models.DecimalField(
        decimal_places=2,
        max_digits=14,
    )
    status = models.PositiveSmallIntegerField(
        choices=StatusTypes.choices, default=StatusTypes.PENDING
    )
    paid_date = models.DateTimeField(blank=True, null=True)
    currency = models.ForeignKey(
        Currency,
        related_name="invoices",
        on_delete=models.PROTECT,
        verbose_name=_("currency"),
        default=settings.DEFAULT_CURRENCY_SIGN,
    )

    def __str__(self):
        return f"{self.code}"

    def save(self, *args, **kwargs):
        if not self.currency:
            self.currency = Currency.objects.get(code=settings.DEFAULT_CURRENCY_SIGN)
        if self.code:
            super().save(*args, **kwargs)
        else:
            while True:
                self.code = f"invoice-{create_random_str(length=6)}"
                try:
                    super().save(*args, **kwargs)
                except IntegrityError:
                    continue
                break

    def set_failed(self):
        if self.status == Invoice.StatusTypes.PENDING:
            self.status = self.StatusTypes.FAILED
            self.save()

    @transaction.atomic
    def set_paid(self):
        if self.status == Invoice.StatusTypes.PENDING:
            user_wallet = Wallet.objects.select_for_update().get(user=self.user)
            user_wallet.balance += self.amount
            user_wallet.save()

            self.status = self.StatusTypes.PAID
            self.paid_date = timezone.now()
            self.save()
