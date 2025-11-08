from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.models import ConnectorModel, ChargerModel, StationModel


class ChargerInline(TabularInline):
    model = ChargerModel
    tab = True
    extra = 0
    fields = ('name', 'cp_id', 'is_active', 'last_health')


@admin.register(StationModel)
class StationAdmin(ModelAdmin):
    inlines = [ChargerInline]
    search_fields = [
        "name",
        "address",
    ]
    list_display = (
        "id",
        "name",
        "address",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "created_at",
    )
    autocomplete_fields = []  # For unfold autocomplete
    
    def get_queryset(self, request):
        """Hodim faqat o'z stationini ko'radi"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.station:
            return qs.filter(id=request.user.station.id)
        return qs.none()
    
    def has_add_permission(self, request):
        """Hodim station qo'sha olmaydi"""
        if request.user.is_superuser:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Hodim station o'chira olmaydi"""
        if request.user.is_superuser:
            return True
        return False


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
        "station",
        "is_active",
        "last_health",
    )
    list_filter = (
        "station",
        "is_active",
    )

    @display(label=True, boolean=True)
    def _is_active(self, obj):
        return obj.is_active
    
    def get_queryset(self, request):
        """Hodim faqat o'z stationidagi chargerlarni ko'radi"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.station:
            return qs.filter(station=request.user.station)
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Hodim faqat o'z stationini tanlashi mumkin"""
        if db_field.name == "station" and not request.user.is_superuser:
            if request.user.station:
                kwargs["queryset"] = StationModel.objects.filter(id=request.user.station.id)
            else:
                kwargs["queryset"] = StationModel.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
    
    def get_queryset(self, request):
        """Hodim faqat o'z stationidagi connectorlarni ko'radi"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.station:
            return qs.filter(charger__station=request.user.station)
        return qs.none()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Hodim faqat o'z stationidagi chargerlarni tanlashi mumkin"""
        if db_field.name == "charger" and not request.user.is_superuser:
            if request.user.station:
                kwargs["queryset"] = ChargerModel.objects.filter(station=request.user.station)
            else:
                kwargs["queryset"] = ChargerModel.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
