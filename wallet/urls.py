from django.urls import include, path

app_name = "wallet"

urlpatterns = [
    path("v1/", include("wallet.api.v1.urls")),
]
