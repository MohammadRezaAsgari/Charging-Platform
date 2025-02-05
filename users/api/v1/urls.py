from django.urls import path

from users.api.v1.views import (
    DecoratedRefreshTokenView,
    LoginPasswordAPIView,
    UserProfileAPIView,
)

app_name = "v1"

urlpatterns = [
    # Login flow API
    path("auth/login-password/", LoginPasswordAPIView.as_view(), name="login_password"),
    # --
    path("auth/refresh/", DecoratedRefreshTokenView.as_view(), name="token_refresh"),
    path("auth/me/", UserProfileAPIView.as_view(), name="user_profile"),
]
