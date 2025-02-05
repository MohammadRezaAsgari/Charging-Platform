from django.urls import include, path

app_name = "user"

urlpatterns = [
    path("v1/", include("users.api.v1.urls", namespace="v1")),
]
