from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class LoginPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class LoginOutputSerializer(serializers.ModelSerializer):
    access = serializers.SerializerMethodField()
    refresh = serializers.SerializerMethodField()
    access_token_expires_at = serializers.SerializerMethodField()

    def _get_token(self, obj):
        # This method only called once
        self.refresh_token = RefreshToken.for_user(obj)
        self.access_token = self.refresh_token.access_token

    def get_access(self, obj) -> str:
        if not hasattr(self, "access_token"):
            self._get_token(obj)
        return str(self.access_token)

    def get_refresh(self, obj) -> str:
        if not hasattr(self, "refresh_token"):
            self._get_token(obj)
        return str(self.refresh_token)

    def get_access_token_expires_at(self, obj):
        if not hasattr(self, "access_token"):
            self._get_token(obj)
        # Calculate expiration time from the access token
        expiration_timestamp = (
            self.access_token["exp"] if "exp" in self.access_token else None
        )
        return expiration_timestamp

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "access",
            "refresh",
            "access_token_expires_at",
        ]


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
        ]


class UserProfileInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
        ]
