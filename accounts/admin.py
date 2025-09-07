# airbnb-clone-project/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    ordering = ("-date_joined",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_active",
        "is_staff",
        "date_joined",
        "last_login",
    )
    list_filter = ("user_type", "is_active", "is_staff", "is_superuser")
    search_fields = ("email", "first_name", "last_name", "phone_number")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "phone_number", "user_type")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "user_type",
                    "phone_number",
                ),
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")

    # Since username is removed, use email as the identifier
    filter_horizontal = ("groups", "user_permissions")
