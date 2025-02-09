from rest_framework import serializers

from users.api.v1.serializers import UserProfileSerializer
from wallet.models import Currency, Invoice, Wallet


class WalletSerializer(serializers.ModelSerializer):

    class Meta:
        model = Wallet
        fields = (
            "currency",
            "balance",
        )


class OutputInvoiceListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = Invoice
        fields = (
            "id",
            "code",
            "user",
            "status",
            "paid_date",
            "amount",
            "currency",
            "created",
            "modified",
        )


class InputInvoiceSerializer(serializers.ModelSerializer):
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())

    class Meta:
        model = Invoice
        fields = (
            "id",
            "amount",
            "currency",
        )
        read_only_fields = ("id",)

    def validate(self, attrs):
        if attrs.get("amount") <= 0:
            raise serializers.ValidationError(
                {"amount": "Amount value cannot be zero or negative!"}
            )
        return super().validate(attrs)


class InvoiceUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = ("status",)
