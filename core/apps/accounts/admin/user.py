from django.contrib.auth import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm  # UserCreationForm,
from unfold.forms import UserChangeForm
from unfold.contrib.filters.admin import AutocompleteSelectFilter


class CustomUserAdmin(admin.UserAdmin, ModelAdmin):
    change_password_form = AdminPasswordChangeForm
    # add_form = UserCreationForm
    form = UserChangeForm
    list_display = (
        "first_name",
        "last_name",
        "phone",
        "role",
        "station",
        "is_staff",
    )
    list_filter = (
        ("station", AutocompleteSelectFilter),
        "role",
        "is_staff",
        "is_active",
    )
    autocomplete_fields = ["groups", "user_permissions", "station"]
    fieldsets = ((None, {"fields": ("phone",)}),) + (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Station"),
            {
                "fields": ("station",),
                "description": "Hodimni stationga biriktirish (Hodim faqat o'z stationidagi ma'lumotlarni ko'radi)",
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                    "role",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


class PermissionAdmin(ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


class GroupAdmin(ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    autocomplete_fields = ("permissions",)


class SmsConfirmAdmin(ModelAdmin):
    list_display = ["phone", "code", "resend_count", "try_count"]
    search_fields = ["phone", "code"]
