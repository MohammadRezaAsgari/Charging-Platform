from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from utils.permissions import IsAuthenticatedAndActive, IsSuperUser
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from wallet.api.v1.serializers import (
    InputInvoiceSerializer,
    InvoiceUpdateSerializer,
    OutputInvoiceListSerializer,
    WalletSerializer,
)
from wallet.models import Invoice, Wallet
from utils.api.responses import success_response, error_response
from utils.api.error_objects import ErrorObject
from utils.api.mixins import BadRequestSerializerMixin
from utils.loggers import stdout_logger


class InvoiceListAPIView(BadRequestSerializerMixin, ListAPIView):
    """
    Gets the list of invoices of the company.
    status options: `1: pending`, `2: paid`, `3: failed`
    """

    permission_classes = [IsAuthenticatedAndActive]
    serializer_class = OutputInvoiceListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "status",
    ]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Invoice.objects.all()
        return self.request.user.invoices.all()

    @extend_schema(
        request=None,
        responses={200: OutputInvoiceListSerializer},
        operation_id="InvoiceList",
        tags=["Wallet"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=InputInvoiceSerializer,
        responses={201: InputInvoiceSerializer},
        operation_id="CreateInvoice",
        tags=["Wallet"],
    )
    def post(self, request, *args, **kwargs):
        """
        creates a new Invoice
        """
        serializer = InputInvoiceSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                error=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if serializer.validated_data.get("currency") != request.user.wallet.currency:
            return error_response(
                error=ErrorObject.NOT_SAME_CURRENCY,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(user=request.user)
        return success_response(
            data=serializer.data, status_code=status.HTTP_201_CREATED
        )


class InvoiceByIDAPIView(BadRequestSerializerMixin, APIView):
    permission_classes = [IsAuthenticatedAndActive, IsSuperUser]

    @extend_schema(
        request=InvoiceUpdateSerializer,
        responses={204: {}},
        auth=None,
        operation_id="UpdateInvoice",
        tags=["Wallet"],
    )
    def patch(self, request, *args, **kwargs):
        """
        admin updates a Invoice status
        """
        try:
            invoice_obj = Invoice.objects.get(id=kwargs.get("invoice_id"))
        except Invoice.DoesNotExist:
            return error_response(
                error=ErrorObject.NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = InvoiceUpdateSerializer(
            invoice_obj, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return self.serializer_error_response(serializer)

        invoice_status = serializer.validated_data.get("status")
        if invoice_status == Invoice.StatusTypes.PAID:
            invoice_obj.set_paid()
        if invoice_status == Invoice.StatusTypes.FAILED:
            invoice_obj.set_failed()

        return success_response(data={}, status_code=status.HTTP_204_NO_CONTENT)


class WalletAPIView(BadRequestSerializerMixin, APIView):
    permission_classes = [IsAuthenticatedAndActive]

    @extend_schema(
        request=None,
        responses={200: WalletSerializer},
        auth=None,
        operation_id="RetrieveWallet",
        tags=["Wallet"],
    )
    def get(self, request, *args, **kwargs):
        wallet_obj = request.user.wallet
        response = WalletSerializer(wallet_obj)
        return success_response(data=response.data, status_code=status.HTTP_200_OK)
