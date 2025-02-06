from rest_framework import serializers

from charge.models import Charging
from users.api.v1.serializers import UserProfileSerializer
from wallet.models import Currency


class OutputChargingListSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer()

    class Meta:
        model = Charging
        fields = (
            "id",
            "user",
            "amount",
            "currency",
            "phone",
            "created",
            "modified",
        )


class InputChargingSerializer(serializers.ModelSerializer):
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())

    class Meta:
        model = Charging
        fields = (
            "amount",
            "currency",
            "phone",
        )

    def validate(self, attrs):
        if attrs.get("amount") <= 0:
            raise serializers.ValidationError(
                {"amount": "Amount value cannot be zero or negative!"}
            )
        return super().validate(attrs)
