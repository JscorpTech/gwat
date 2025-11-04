# type: ignore
import logging
from celery import shared_task
from celery.utils.time import timedelta
from django.utils import timezone

from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models.station import ChargerModel
from core.apps.api.schemas.events import StopTransaction
from core.apps.api.services.ocpp import stop_transaction
from core.apps.api.services.ws import ws_connector_event


@shared_task
def check_fail_chargers():
    """5 daqiqa ichida health yubormagan chargerlarni o'chirish"""
    threshold = timezone.now() - timedelta(minutes=5)
    chargers = ChargerModel.objects.filter(last_health__lt=threshold)
    logging.info("checking fail chargers found=%s", chargers.count())
    for charger in chargers:
        logging.warning("Charger health yubormagani uchun transaction va connectorlar o'chirildi charger=%s", charger)
        for conn in charger.connectors.filter(
            status__in=[
                ConnectorStatusEnum.AVAILABLE.value,
                ConnectorStatusEnum.CHARGING.value,
                ConnectorStatusEnum.PREPARING.value,
            ]
        ):
            conn.status = ConnectorStatusEnum.FAULTED.value
            conn.save()
            for transaction in conn.transactions.filter(
                status__in=[TransactionStatusEnum.CHARGING.value, TransactionStatusEnum.PENDING.value]
            ):
                data = StopTransaction(
                    charger=transaction.conn.charger.pk,
                    transaction_id=transaction.pk,
                    reason="",
                    meter_stop=transaction.last_meter,
                )
                logging.info(
                    "Transaction fail transaction=%s conn=%s charger=%s",
                    transaction,
                    conn,
                    charger,
                )
                stop_transaction(transaction, TransactionStatusEnum.PENDING, data, force_stop=True)
            ws_connector_event(conn)
