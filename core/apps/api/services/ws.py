from core.apps.api.models.station import ChargerModel, ConnectorModel
from core.apps.api.models.transaction import TransactionModel
from core.apps.websocket.schemas.events import ConnectorStatus, Health, TransactionMetrics, WsEvents
from core.apps.websocket.services.services import send_event
from core.apps.websocket.schemas.events import WsEventsEnum


def ws_transaction_event(transaction: TransactionModel):
    """Frontendga Websocket orqali eventlarni yuborish

    Args:
        transaction: [TODO:description]
    """
    conn = transaction.conn
    metrics = TransactionMetrics(
        id=transaction.pk,
        charger=conn.charger.pk,
        conn=conn.pk,
        meter_consumed=transaction.meter_consumed,
        price=str(transaction.amount),
        limit=str(transaction.limit) if transaction.limit is not None else None,
        power=conn.power,
        status=transaction.status,
    )
    payload = WsEvents(event=WsEventsEnum.TRANSACTION_METRICS, data=metrics)

    send_event("charger_events", payload.model_dump())


def ws_health_event(charger: ChargerModel):
    """Health event

    Args:
        charger: [TODO:description]
    """
    data = Health(
        charger=charger.pk,
        last_health=charger.last_health.isoformat() if charger.last_health is not None else "",
    )
    payload = WsEvents(event=WsEventsEnum.HEALTH, data=data)
    send_event("charger_events", payload.model_dump())


def ws_connector_event(conn: ConnectorModel):
    """Websocket orqali conn statusi haqida event yuboradi

    Args:
        conn: [TODO:description]
    """
    data = ConnectorStatus(
        conn=conn.pk,
        status=conn.status,
        charger=conn.charger.pk,
    )
    payload = WsEvents(event=WsEventsEnum.CONNECTOR_STATUS, data=data)

    send_event("charger_events", payload.model_dump())
