from django.urls import path

from wallet.api.v1.views import (
    InvoiceListAPIView,
    InvoiceByIDAPIView,
    WalletAPIView,
)

app_name = "v1"

urlpatterns = [
    path("wallet/invoices/", InvoiceListAPIView.as_view(), name="invoice_list"),
    path(
        "wallet/invoices/<int:invoice_id>/",
        InvoiceByIDAPIView.as_view(),
        name="invoice_detail",
    ),
    path("wallet/balance/", WalletAPIView.as_view(), name="wallet"),
]
