from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as User_Admin

from .forms import UserCreationForm, UserChangeForm
from .models import User


class UserAdmin(User_Admin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ("email", "is_staff", "is_active", "created_at")
    list_filter = ("email", "is_staff", "is_active", "created_at")
    fieldsets = (
        (None, {"fields": ("email", "password", "position")}),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
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
                    "is_staff",
                    "is_active",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)


class PICManager(admin.ModelAdmin):
    list_display = ["user", "created_at"]


admin.site.register(User, UserAdmin)
