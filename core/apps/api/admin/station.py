from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.models import ConnectorModel, ChargerModel


class ConnectorInline(TabularInline):
    model = ConnectorModel
    tab = True
    extra = 0


@admin.register(ChargerModel)
class ChargerAdmin(ModelAdmin):
    inlines = [ConnectorInline]
    search_fields = [
        "name",
    ]
    list_display = (
        "id",
        "name",
        "cp_id",
        "is_active",
        "last_health",
    )

    @display(label=True, boolean=True)
    def _is_active(self, obj):
        return obj.is_active


@admin.register(ConnectorModel)
class ConnectorAdmin(ModelAdmin):
    search_fields = [
        "name",
        "charger__name",
    ]
    list_display = (
        "id",
        "name",
        "conn_id",
        "charger",
        "power",
        "_status",
    )

    @display(
        label={
            ConnectorStatusEnum.AVAILABLE.value: "info",
            ConnectorStatusEnum.PREPARING.value: "success",
            ConnectorStatusEnum.CHARGING.value: "primary",
            ConnectorStatusEnum.FINISHING.value: "warning",
        }
    )
    def _status(self, obj):
        return obj.status
