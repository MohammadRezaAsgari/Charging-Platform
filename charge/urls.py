from django.urls import include, path

app_name = "charge"

urlpatterns = [
    path("v1/", include("charge.api.v1.urls")),
]
