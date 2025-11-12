from django_filters import rest_framework as filters
import django_filters

from core.apps.api.models import TransactionModel


class TransactionFilter(filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        model = TransactionModel
        fields = [
            "conn",
            "conn__charger",
            "conn__charger__station",
            "status",
            "is_force_stop",
        ]
