from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from core.apps.api.models import ConnectorModel, ChargerModel


class ConnectorInline(TabularInline):
    model = ConnectorModel
    tab = True
    extra = 0


@admin.register(ChargerModel)
class ChargerAdmin(ModelAdmin):
    inlines = [ConnectorInline]
    list_display = (
        "id",
        "__str__",
    )


@admin.register(ConnectorModel)
class ConnectorAdmin(ModelAdmin):
    list_display = (
        "id",
        "__str__",
    )
