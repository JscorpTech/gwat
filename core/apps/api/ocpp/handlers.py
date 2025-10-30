from core.apps.api.enums.transaction import TransactionStatusEnum
from django.utils import timezone
from core.apps.api.models.station import ConnectorModel
from core.apps.api.models.transaction import TransactionModel
import logging
from core.apps.api.schemas import Events

from core.apps.api.schemas.events import (
    ChangeConnectorStatus,
    MeterValue,
    StartTransaction,
    StopTransaction,
)
from core.apps.api.services.payment import calc_energy_price
from core.apps.api.services.station import get_meter, parse_meter_values, remote_stop_transaction


class OcppHandler:

    def change_connector_status(self, event: Events):
        """
        Args:
            event (Evens):
        Returns:
            None:
        """
        data = ChangeConnectorStatus.model_validate(event.data)
        conn = ConnectorModel.objects.filter(conn_id=data.conn, station__cp_id=data.charger).first()
        if conn is None:
            logging.error("conn not found pk=%s", data.conn)
            return
        conn.status = data.status
        conn.save()
        logging.info("conn status updated conn=%s status=%s", conn.pk, conn.status)

    def start_transaction(self, event: Events):
        """
        Args:
            event (Events):
        Returns:
            None:
        """
        data = StartTransaction.model_validate(event.data)
        transaction = TransactionModel.objects.filter(tag=data.tag, conn__conn_id=data.conn).first()
        if transaction is None:
            logging.error("Event Start Transaction not found tag=%s conn=%s", data.tag, data.conn)
            return
        transaction.status = TransactionStatusEnum.CHARGING.value
        transaction.meter_start = data.meter_start
        transaction.save()
        logging.info("start transaction conn=%s tag=%s", data.conn, data.tag)

    def stop_transaction(self, event: Events):
        """
        Args:
            event (Evens):
        Returns:
            None:
        """
        data = StopTransaction.model_validate(event.data)
        transaction = TransactionModel.objects.filter(pk=data.transaction_id).first()
        if transaction is None:
            logging.error("Stop event transaction not found transaction_id=%s", data.transaction_id)
            return
        transaction.status = TransactionStatusEnum.COMPLATE.value
        transaction.meter_stop = data.meter_stop
        if transaction.meter_stop < transaction.meter_start:
            logging.critical("Transaction meter_stop meter_start dan kichik bu daxshatli xato to'g'irlash kerak")
            transaction.meter_consumed = 0
        else:
            transaction.meter_consumed = transaction.meter_stop - transaction.meter_start
        transaction.end_date = timezone.now()
        transaction.amount = calc_energy_price(transaction.meter_consumed)
        transaction.save()
        logging.info(
            "stop transaction charger=%s transaction=%s reason=%s", data.charger, data.transaction_id, data.reason
        )

    def meter_value(self, event: Events):
        """
        Args:
            event (Events):
        Returns:
            None:
        """
        data = MeterValue.model_validate(event.data)
        transaction = TransactionModel.objects.filter(pk=data.transaction_id).first()
        if transaction is None:
            logging.error("Meter value event transaction not found transaction_id=%s", data.transaction_id)
            return
        meter_value = parse_meter_values(data.meter_value)[0]
        meter_current = get_meter(meter_value)
        meter_start = transaction.meter_start
        # meter_consumed: ishlatilgan energiya
        meter_consumed = meter_current - meter_start
        price = calc_energy_price(meter_consumed)
        transaction.meter_consumed = meter_consumed
        transaction.save()

        if transaction.limit != -1.00:
            if price >= transaction.limit:
                charger = transaction.conn.station.cp_id
                remote_stop_transaction(charger, transaction.pk)
                logging.info("Limitga yetib keldi limit=%s curent_price=%s", transaction.limit, price)
