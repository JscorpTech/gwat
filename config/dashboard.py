from django.db.models import Sum, Count, Q
from django.utils.translation import gettext_lazy as _
import json
from core.apps.api.models.transaction import TransactionModel
from core.apps.api.models.station import ConnectorModel, ChargerModel, StationModel
from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.enums.connectors import ConnectorStatusEnum


def dashboard_callback(request, context):
    """
    Dashboard callback for admin panel home page
    Returns dynamic statistics with charts and progress bars
    """
    # Get total statistics
    transaction_stats = TransactionModel.objects.aggregate(
        total_amount=Sum("amount"),
        total_transactions=Count("id"),
        total_energy=Sum("meter_consumed"),
        completed=Count("id", filter=Q(status=TransactionStatusEnum.COMPLATE.value)),
        charging=Count("id", filter=Q(status=TransactionStatusEnum.CHARGING.value)),
        pending=Count("id", filter=Q(status=TransactionStatusEnum.PENDING.value)),
        failed=Count("id", filter=Q(status=TransactionStatusEnum.FAIL.value)),
        stopped=Count("id", filter=Q(status=TransactionStatusEnum.STOP.value)),
    )

    # Get charger statistics
    charger_stats = ChargerModel.objects.aggregate(
        total_chargers=Count("id"),
        active_chargers=Count("id", filter=Q(is_active=True)),
    )
    
    # Get station statistics
    station_stats = StationModel.objects.aggregate(
        total_stations=Count("id"),
        active_stations=Count("id", filter=Q(is_active=True)),
    )

    # Get connector statistics
    connector_stats = ConnectorModel.objects.aggregate(
        total_connectors=Count("id"),
        available=Count("id", filter=Q(status=ConnectorStatusEnum.AVAILABLE.value)),
        charging_connectors=Count("id", filter=Q(status=ConnectorStatusEnum.CHARGING.value)),
        preparing=Count("id", filter=Q(status=ConnectorStatusEnum.PREPARING.value)),
        finishing=Count("id", filter=Q(status=ConnectorStatusEnum.FINISHING.value)),
        unavailable=Count("id", filter=Q(status=ConnectorStatusEnum.UNAVAILABLE.value)),
    )
    
    # Get revenue by charger
    chargers_revenue = ChargerModel.objects.annotate(
        revenue=Sum('connectors__transactions__amount')
    ).values('id', 'name', 'revenue').order_by('-revenue')[:10]  # Top 10 chargers
    
    charger_names = []
    charger_revenues = []
    for c in chargers_revenue:
        if c['revenue'] and c['revenue'] > 0:
            charger_names.append(str(c['name']) if c['name'] else f"Charger #{c['id']}")
            charger_revenues.append(float(c['revenue']))
    
    # Get revenue by station
    stations_revenue = StationModel.objects.annotate(
        revenue=Sum('chargers__connectors__transactions__amount')
    ).values('id', 'name', 'revenue').order_by('-revenue')[:10]  # Top 10 stations
    
    station_names = []
    station_revenues = []
    for s in stations_revenue:
        if s['revenue'] and s['revenue'] > 0:
            station_names.append(str(s['name']) if s['name'] else f"Station #{s['id']}")
            station_revenues.append(float(s['revenue']))

    # Format energy to kWh
    total_energy = transaction_stats.get("total_energy") or 0
    total_energy_kwh = float(total_energy) / 1000  # Convert Wh to kWh

    # Format amount
    total_amount = transaction_stats.get("total_amount") or 0
    total_transactions = transaction_stats.get("total_transactions", 0)

    # Calculate percentages for progress bars
    total_chargers = charger_stats.get("total_chargers", 0)
    active_chargers = charger_stats.get("active_chargers", 0)
    charger_active_percent = (active_chargers / total_chargers * 100) if total_chargers > 0 else 0
    
    total_stations = station_stats.get("total_stations", 0)
    active_stations = station_stats.get("active_stations", 0)
    station_active_percent = (active_stations / total_stations * 100) if total_stations > 0 else 0

    total_connectors = connector_stats.get("total_connectors", 0)
    available_connectors = connector_stats.get("available", 0)
    connector_available_percent = (available_connectors / total_connectors * 100) if total_connectors > 0 else 0

    # Transaction status percentages
    completed = transaction_stats.get("completed", 0)
    charging = transaction_stats.get("charging", 0)
    pending = transaction_stats.get("pending", 0)
    failed = transaction_stats.get("failed", 0)
    stopped = transaction_stats.get("stopped", 0)

    completed_percent = (completed / total_transactions * 100) if total_transactions > 0 else 0

    # Calculate max value for progress bars
    max_transaction_status = max(completed, charging, pending, failed, stopped) if total_transactions > 0 else 1
    max_connector_status = (
        max(
            connector_stats.get("available", 0),
            connector_stats.get("charging_connectors", 0),
            connector_stats.get("preparing", 0),
            connector_stats.get("finishing", 0),
            connector_stats.get("unavailable", 0),
        )
        if total_connectors > 0
        else 1
    )

    # Main statistics cards
    context.update(
        {
            "kpi": [
                {
                    "title": str(_("Jami Summa")),
                    "metric": f"{float(total_amount):,.0f}",
                    "footer": str(_("so'm")),
                    "icon": "payments",
                    "icon_color": "#10b981",
                    "icon_bg": "#d1fae5",
                },
                {
                    "title": str(_("Jami Transactionlar")),
                    "metric": f"{total_transactions:,}",
                    "footer": f"{completed_percent:.1f}% tugallangan",
                    "icon": "receipt_long",
                    "icon_color": "#3b82f6",
                    "icon_bg": "#dbeafe",
                },
                {
                    "title": str(_("Jami Energiya")),
                    "metric": f"{total_energy_kwh:,.1f}",
                    "footer": str(_("kWh")),
                    "icon": "bolt",
                    "icon_color": "#a855f7",
                    "icon_bg": "#f3e8ff",
                },
                {
                    "title": str(_("Faol Stationlar")),
                    "metric": f"{active_stations}/{total_stations}",
                    "footer": f"{station_active_percent:.1f}% faol",
                    "progress": station_active_percent,
                    "progress_title": str(_("Station aktivligi")),
                    "icon": "location_on",
                    "icon_color": "#ef4444",
                    "icon_bg": "#fee2e2",
                },
                {
                    "title": str(_("Faol Chargerlar")),
                    "metric": f"{active_chargers}/{total_chargers}",
                    "footer": f"{charger_active_percent:.1f}% faol",
                    "progress": charger_active_percent,
                    "progress_title": str(_("Charger aktivligi")),
                    "icon": "ev_station",
                    "icon_color": "#6366f1",
                    "icon_bg": "#e0e7ff",
                },
            ],
            "charts": [
                {
                    "id": "transactionChart",
                    "type": "doughnut",
                    "title": str(_("Transaction Status Taqsimoti")),
                    "description": str(_("Transactionlar status bo'yicha")),
                    "labels": json.dumps(
                        [str(_("Tugallangan")), str(_("Charging")), str(_("Pending")), str(_("Failed")), str(_("Stopped"))]
                    ),
                    "datasets": {
                        "label": str(_("Transactions")),
                        "data": json.dumps([completed, charging, pending, failed, stopped]),
                        "backgroundColor": json.dumps(["#10b981", "#3b82f6", "#eab308", "#ef4444", "#dc2626"]),
                    },
                },
                {
                    "id": "connectorChart",
                    "type": "doughnut",
                    "title": str(_("Connector Status Taqsimoti")),
                    "description": str(_("Connectorlar status bo'yicha")),
                    "labels": json.dumps(
                        [
                            str(_("Available")),
                            str(_("Charging")),
                            str(_("Preparing")),
                            str(_("Finishing")),
                            str(_("Unavailable")),
                        ]
                    ),
                    "datasets": {
                        "label": str(_("Connectors")),
                        "data": json.dumps(
                            [
                                connector_stats.get('available', 0),
                                connector_stats.get('charging_connectors', 0),
                                connector_stats.get('preparing', 0),
                                connector_stats.get('finishing', 0),
                                connector_stats.get('unavailable', 0),
                            ]
                        ),
                        "backgroundColor": json.dumps(
                            ["#10b981", "#3b82f6", "#eab308", "#a855f7", "#ef4444"]
                        ),
                    },
                },
                {
                    "id": "stationRevenueChart",
                    "type": "bar",
                    "title": str(_("Stationlar Daromadi (Top 10)")),
                    "description": str(_("Eng ko'p daromad keltirgan stationlar")),
                    "labels": json.dumps(station_names if station_names else ["Ma'lumot yo'q"]),
                    "datasets": {
                        "label": str(_("Daromad (so'm)")),
                        "data": json.dumps(station_revenues if station_revenues else [0]),
                        "backgroundColor": json.dumps(["#10b981"] * (len(station_revenues) if station_revenues else 1)),
                    },
                },
                {
                    "id": "chargerRevenueChart",
                    "type": "bar",
                    "title": str(_("Chargerlar Daromadi (Top 10)")),
                    "description": str(_("Eng ko'p daromad keltirgan chargerlar")),
                    "labels": json.dumps(charger_names if charger_names else ["Ma'lumot yo'q"]),
                    "datasets": {
                        "label": str(_("Daromad (so'm)")),
                        "data": json.dumps(charger_revenues if charger_revenues else [0]),
                        "backgroundColor": json.dumps(["#3b82f6"] * (len(charger_revenues) if charger_revenues else 1)),
                    },
                },
            ],
        }
    )

    return context
