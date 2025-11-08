from django.db.models import Sum, Count, Q
from django.utils.translation import gettext_lazy as _
from core.apps.api.models.transaction import TransactionModel
from core.apps.api.models.station import ConnectorModel, ChargerModel
from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.enums.connectors import ConnectorStatusEnum


def dashboard_callback(request, context):
    """
    Dashboard callback for admin panel home page
    Returns dynamic statistics cards
    """
    # Get total statistics
    transaction_stats = TransactionModel.objects.aggregate(
        total_amount=Sum('amount'),
        total_transactions=Count('id'),
        total_energy=Sum('meter_consumed'),
        completed=Count('id', filter=Q(status=TransactionStatusEnum.COMPLATE.value)),
        charging=Count('id', filter=Q(status=TransactionStatusEnum.CHARGING.value)),
    )
    
    # Get charger statistics
    charger_stats = ChargerModel.objects.aggregate(
        total_chargers=Count('id'),
        active_chargers=Count('id', filter=Q(is_active=True)),
    )
    
    # Get connector statistics
    connector_stats = ConnectorModel.objects.aggregate(
        total_connectors=Count('id'),
        available=Count('id', filter=Q(status=ConnectorStatusEnum.AVAILABLE.value)),
        charging_connectors=Count('id', filter=Q(status=ConnectorStatusEnum.CHARGING.value)),
    )
    
    # Format energy to kWh
    total_energy = transaction_stats.get('total_energy') or 0
    total_energy_kwh = float(total_energy) / 1000  # Convert Wh to kWh
    
    # Format amount
    total_amount = transaction_stats.get('total_amount') or 0
    
    cards = [
        {
            "title": _("Jami Summa"),
            "value": f"{float(total_amount):,.2f} so'm",
            "color": "green",
        },
        {
            "title": _("Jami Transactionlar"),
            "value": transaction_stats.get('total_transactions', 0),
            "color": "blue",
        },
        {
            "title": _("Jami Energiya"),
            "value": f"{total_energy_kwh:,.2f} kWh",
            "color": "purple",
        },
        {
            "title": _("Charging"),
            "value": transaction_stats.get('charging', 0),
            "color": "blue",
        },
        {
            "title": _("Tugallangan"),
            "value": transaction_stats.get('completed', 0),
            "color": "green",
        },
        {
            "title": _("Jami Chargerlar"),
            "value": charger_stats.get('total_chargers', 0),
            "color": "indigo",
        },
        {
            "title": _("Faol Chargerlar"),
            "value": charger_stats.get('active_chargers', 0),
            "color": "green",
        },
        {
            "title": _("Jami Connectorlar"),
            "value": connector_stats.get('total_connectors', 0),
            "color": "indigo",
        },
        {
            "title": _("Available Connectors"),
            "value": connector_stats.get('available', 0),
            "color": "green",
        },
        {
            "title": _("Charging Connectors"),
            "value": connector_stats.get('charging_connectors', 0),
            "color": "blue",
        },
    ]
    
    context.update({
        "cards": cards,
    })
    
    return context
