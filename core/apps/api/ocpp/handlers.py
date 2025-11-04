from core.apps.api.enums.transaction import TransactionStatusEnum
from django.utils import timezone
from core.apps.api.models.station import ChargerModel, ConnectorModel
from core.apps.api.models.transaction import TransactionModel
import logging
from core.apps.api.schemas import Events

from core.apps.api.schemas.events import (
    ChangeConnectorStatus,
    DataTransfer,
    Health,
    MeterValue,
    StartTransaction,
    StopTransaction,
)
from core.apps.api.services.payment import calc_energy_price
from core.apps.api.services.ocpp import get_meter, parse_meter_values, remote_stop_transaction, stop_transaction
from core.apps.api.services.ws import ws_connector_event, ws_health_event, ws_transaction_event


class OcppHandler:

    def change_connector_status(self, event: Events):
        """
        Args:
            event (Evens):
        Returns:
            None:
        """
        data = ChangeConnectorStatus.model_validate(event.data)
        conn = ConnectorModel.objects.filter(conn_id=data.conn, charger__cp_id=data.charger).first()
        if conn is None:
            logging.error("conn not found conn=%s charger=%s", data.conn, data.charger)
            return
        conn.status = data.status
        conn.save()
        ws_connector_event(conn)
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
        ws_transaction_event(transaction)
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
        # INFO: stop_transaction: transactionni yakunlash va notification yuborish
        # boshqa joylarda ham kerak bo'lgani uchun alohida ko'chirilgan
        # boshqa eventlar handler ichida faqat stop_transaction alohida
        stop_transaction(transaction, TransactionStatusEnum.COMPLATE, data)

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
        meter_value = parse_meter_values(data.meter_value)
        if len(meter_value) <= 0:
            logging.critical("MeterValue topilmadi")
            return
        meter_value = meter_value[0]
        meter_current = get_meter(meter_value)
        meter_start = transaction.meter_start
        # meter_consumed: ishlatilgan energiya
        meter_consumed = meter_current - meter_start
        price = calc_energy_price(meter_consumed)
        transaction.amount = price
        transaction.meter_consumed = meter_consumed
        transaction.last_meter = meter_current
        transaction.save()
        ws_transaction_event(transaction)

        if transaction.limit is not None:
            if price >= transaction.limit:
                charger = transaction.conn.charger.cp_id
                resp = remote_stop_transaction(charger, transaction.pk)
                logging.info("Limitga yetib keldi limit=%s curent_price=%s success=%s", transaction.limit, price, resp)

    def data_transfer(self, event: Events):
        """DataTransfer

        Args:
            event: [TODO:description]
        """
        print(event)

    def health(self, event: Events):
        """qurilma activligini tekshirish

        Args:
            event: [TODO:description]
        """
        data = Health.model_validate(event.data)
        charger = ChargerModel.objects.filter(cp_id=data.charger).first()
        if charger is None:
            logging.error("health charger not found charger=%s", charger)
            return
        date = timezone.now()
        charger.last_health = date
        charger.save()
        ws_health_event(charger)
        logging.info("charger health charger=%s date=%s", charger, date)
