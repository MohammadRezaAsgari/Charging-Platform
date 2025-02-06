from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from charge.models import Charging
from utils.permissions import IsAuthenticatedAndActive
from django_filters.rest_framework import DjangoFilterBackend

from charge.api.v1.serializers import (
    OutputChargingListSerializer,
    InputChargingSerializer,
)
from utils.api.responses import success_response, error_response
from utils.api.error_objects import ErrorObject
from utils.api.mixins import BadRequestSerializerMixin
from utils.loggers import stdout_logger


class ChargingListAPIView(BadRequestSerializerMixin, ListAPIView):
    permission_classes = [IsAuthenticatedAndActive]
    serializer_class = OutputChargingListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "currency",
    ]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Charging.objects.all()
        return self.request.user.chargings.all()

    @extend_schema(
        request=None,
        responses={200: OutputChargingListSerializer},
        operation_id="CharginsList",
        tags=["Charge"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        request=InputChargingSerializer,
        responses={201: InputChargingSerializer},
        operation_id="CreateCharging",
        tags=["Charge"],
    )
    def post(self, request, *args, **kwargs):
        serializer = InputChargingSerializer(data=request.data)
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

        if not request.user.wallet.has_enough_credit(
            serializer.validated_data.get("amount")
        ):
            return error_response(
                error=ErrorObject.NOT_ENOUGH_BALANCE,
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
            )

        request.user.charge_phone(**serializer.validated_data)
        return success_response(
            data=serializer.data, status_code=status.HTTP_201_CREATED
        )
