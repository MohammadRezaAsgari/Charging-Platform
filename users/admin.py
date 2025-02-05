from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = [
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_superuser",
    ]
    list_filter = [
        "is_active",
        "is_superuser",
    ]
    search_fields = ["username", "first_name", "last_name"]
    list_display_links = ["username"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "is_staff",
                ),
            },
        ),
    )


admin.site.register(User, CustomUserAdmin)
