from django.contrib import admin

from wallet.models import Currency, Invoice, Wallet


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "user",
        "status",
    )


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin): ...


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin): ...
