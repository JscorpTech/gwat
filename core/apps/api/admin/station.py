from django.contrib import admin
from unfold.admin import ModelAdmin

from core.apps.api.models import ConnectorModel, StationModel


@admin.register(StationModel)
class StationAdmin(ModelAdmin):
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
