from django.urls import path

from charge.api.v1.views import (
    ChargingListAPIView,
)

app_name = "v1"

urlpatterns = [
    path("charge/chargings/", ChargingListAPIView.as_view(), name="charging_list"),
]
