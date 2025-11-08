from decimal import ROUND_HALF_UP, Decimal
from django.contrib import admin
from django.db.models import Sum, Count, Q
from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.contrib.filters.admin import (
    RangeDateTimeFilter,
    AutocompleteSelectFilter,
    MultipleChoicesDropdownFilter,
    BooleanRadioFilter,
)

from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models import TransactionModel
from unfold.components import register_component, BaseComponent


@register_component
class TransactionStatsComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Stats are now passed directly from changelist_view
        return context


@admin.register(TransactionModel)
class TransactionAdmin(ModelAdmin):
    change_list_template = "admin/api/transaction/change_list.html"

    list_filter = (
        ("created_at", RangeDateTimeFilter),
        ("user", AutocompleteSelectFilter),
        ("status", MultipleChoicesDropdownFilter),
        ("conn__charger", AutocompleteSelectFilter),
        ("conn", AutocompleteSelectFilter),
        ("is_force_stop", BooleanRadioFilter),
    )
    list_filter_submit = True
    list_display = (
        "id",
        "user",
        "conn",
        "_status",
        "amount",
        "limit",
        "soc",
        "_meter_consumed",
        "_last_meter",
        "is_force_stop",
        "tag",
        "created_at",
    )

    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
            
        response = super().changelist_view(request, extra_context)
        
        # Calculate statistics from the filtered queryset
        if hasattr(response, 'context_data') and response.context_data:
            cl = response.context_data.get('cl')
            if cl:
                queryset = cl.queryset
                
                stats = queryset.aggregate(
                    total_amount=Sum('amount'),
                    total_transactions=Count('id'),
                    total_energy_consumed=Sum('meter_consumed'),
                    completed_count=Count('id', filter=Q(status=TransactionStatusEnum.COMPLATE.value)),
                    charging_count=Count('id', filter=Q(status=TransactionStatusEnum.CHARGING.value)),
                    pending_count=Count('id', filter=Q(status=TransactionStatusEnum.PENDING.value)),
                    failed_count=Count('id', filter=Q(status=TransactionStatusEnum.FAIL.value)),
                    stopped_count=Count('id', filter=Q(status=TransactionStatusEnum.STOP.value)),
                )
                
                response.context_data['transaction_stats'] = stats
        
        return response
    
    def get_queryset(self, request):
        """Hodim faqat o'z stationidagi transactionlarni ko'radi"""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.station:
            return qs.filter(conn__charger__station=request.user.station)
        return qs.none()

    @display(
        label={
            TransactionStatusEnum.CHARGING.value: "info",
            TransactionStatusEnum.COMPLATE.value: "success",
            TransactionStatusEnum.PENDING.value: "warning",
            TransactionStatusEnum.FAIL.value: "danger",
            TransactionStatusEnum.STOP.value: "danger",
        }
    )
    def _status(self, obj):
        return obj.status

    @display(label=True)
    def _meter_consumed(self, obj):
        return obj.meter_consumed.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)

    @display(label=True)
    def _last_meter(self, obj):
        return obj.last_meter.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
