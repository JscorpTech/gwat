from django.conf import settings
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from core.apps.customer.models import Client
from core.apps.customer.models.tenants import Domain


class DomainInline(TabularInline):
    model = Domain
    extra = 1


@admin.register(Client)
class ClientAdmin(ModelAdmin):
    inlines = [DomainInline]
    list_display = ("name", "paid_until")

    def log_addition(self, *args, **kwargs):
        return

    def log_change(self, *args, **kwargs):
        return

    def log_deletion(self, *args, **kwargs):
        return

    def has_view_permission(self, request, view=None):
        if request.tenant.schema_name == settings.TENANT_ADMIN_SCHEMA:
            return True
        else:
            return False

    def has_add_permission(self, request, view=None):
        if request.tenant.schema_name == settings.TENANT_ADMIN_SCHEMA:
            return True
        else:
            return False

    def has_change_permission(self, request, view=None):
        if request.tenant.schema_name == settings.TENANT_ADMIN_SCHEMA:
            return True
        else:
            return False

    def has_delete_permission(self, request, view=None):
        if request.tenant.schema_name == settings.TENANT_ADMIN_SCHEMA:
            return True
        else:
            return False

    def has_view_or_change_permission(self, request, view=None):
        if request.tenant.schema_name == settings.TENANT_ADMIN_SCHEMA:
            return True
        else:
            return False
