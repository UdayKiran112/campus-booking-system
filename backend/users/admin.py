from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "role", "department", "verified", "is_active"]
    list_filter = ["role", "verified", "is_active", "department"]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "employee_id",
        "student_id",
    ]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Role & Department", {"fields": ("role", "department", "verified")}),
        (
            "Additional Info",
            {
                "fields": (
                    "phone_number",
                    "employee_id",
                    "student_id",
                    "organization_name",
                )
            },
        ),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Role & Department", {"fields": ("role", "department")}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "no_show_count",
        "total_bookings",
        "successful_bookings",
        "reliability_score",
    ]
    search_fields = ["user__username", "user__email"]
    readonly_fields = ["reliability_score"]
