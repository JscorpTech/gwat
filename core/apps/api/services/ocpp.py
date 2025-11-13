# type: ignore
from decimal import Decimal
import logging
from typing import Dict, List, Optional
from django.utils import timezone
from pydantic import BaseModel
import redis
from config.env import env
from core.apps.api.enums.connectors import ConnectorStatusEnum
from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models.station import ChargerModel, ConnectorModel
from core.apps.api.models.transaction import TransactionModel
from random import randrange
from django.utils.translation import gettext as _

from core.apps.api.schemas.events import MeterValueData, SampledValue, StopTransaction
from core.apps.api.schemas.remote_commands import (
    RemoteCommandStatus,
    RemoteStartTransaction,
    RemoteStopTransaction,
    RemoteCommands,
)
from core.apps.api.services.payment import calc_energy_price
from core.apps.api.services.ws import ws_connector_event, ws_transaction_event
from httpx import Client


client = redis.Redis(host=env.str("REDIS_HOST", "redis"))


def send_command(charger_id: str, command: str, data: BaseModel) -> dict:
    client = Client(base_url=env.str("OCPP_URL"))
    resp = client.post(
        "/command/",
        json={
            "cp_id": str(charger_id),
            "command": command,
            "data": data.model_dump(),
        },
    )
    return resp.json()


def generate_str(length=10):
    """generate random chars

    Args:
        length (int):
    """
    chars = "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    return "".join([chars[randrange(1, len(chars))] for _ in range(length)])


def generate_tag(length=10) -> str:
    """Generate transaction tag

    Args:
        length (int):
    Returns:
        str: random chars
    """
    tag = generate_str(length)
    if TransactionModel.objects.filter(tag=tag).exists():
        return generate_tag()
    return tag


def remote_start_transaction(host: str, charger_id: str, conn_id: int, tag: str) -> (bool, str):
    """
    Args:
        charger_id (str): charger point id
        conn_id (int): connector id
        tag (str):
    Returns:
        None:
    """
    logging.info("Remote command start transaction charger=%s conn=%s tag=%s", charger_id, conn_id, tag)
    try:
        resp = send_command(
            make_charger_id(host, charger_id),
            RemoteCommands.REMOTE_START_TRANSACTION.value,
            RemoteStartTransaction(tag=tag, connector_id=str(conn_id)),
        )
        if resp.get("status") == RemoteCommandStatus.ACCEPTED.value:
            return True, ""
        return False, resp.get("detail")
    except Exception as e:
        logging.error(e)
        return False, _("Internal server error")


def remote_stop_transaction(host: str, charger_id: int, transaction_id: int) -> (bool, str):
    """
    Args:
        charger_id (str): charger point id
        transaction_id (str): transaction id
    Returns:
        None:
    """
    logging.info("Remote command stop transaction charger=%s transaction=%s", charger_id, transaction_id)
    try:
        resp = send_command(
            make_charger_id(host, charger_id),
            RemoteCommands.REMOTE_STOP_TRANSACTION.value,
            RemoteStopTransaction(transaction_id=transaction_id),
        )
        if resp.get("status") == RemoteCommandStatus.ACCEPTED.value:
            return True, ""
        return False, resp.get("detail")
    except Exception as e:
        logging.error(e)
        return False, _("Internal server error")


def parse_meter_values(data: List[MeterValueData]) -> List[Dict[str, SampledValue]]:
    """parse ocpp1.6 meter values list -> dict

    Args:
        data: [TODO:description]

    Returns:
        [TODO:description]
    """
    meter_values = []
    for item in data:
        sampledValue = {}
        for value in item.sampledValue:
            sampledValue[value.measurand] = value
        meter_values.append(sampledValue)
    return meter_values


def get_soc(meter_value: Dict[str, SampledValue]) -> int:
    return 90


def get_meter(data: Dict[str, SampledValue]) -> Decimal:
    """Sarflangan energiyani olish

    Args:
        data: [TODO:description]

    Returns:
        [TODO:description]
    """
    value = data["Energy.Active.Import.Register"].value
    if value == "":
        return 0
    try:
        return Decimal(value)
    except ValueError as err:
        logging.critical("meter value olishda xatolik", err)
        return 0


def stop_transaction(
    transaction: TransactionModel,
    status: TransactionStatusEnum,
    host: str,
    data: Optional[StopTransaction] = None,
    force_stop: bool = False,
):
    """Transactionni tugatish databaseni yangilaydi va notification yuboradi

    Args:
        transaction: [TODO:description]
        status: [TODO:description]
        data: Agar data null bo'lsa avtomatik transactiondagi malumotlardan foydalanib to'ldiriladi
        force_stop: majburiy to'xtatilganini belgilash
    """
    if data is None:
        data = StopTransaction(
            charger="%s:%s" % (host, transaction.conn.charger.pk),
            transaction_id=transaction.pk,
            reason="",
            meter_stop=transaction.last_meter,
        )

    transaction.status = status.value
    transaction.meter_stop = data.meter_stop
    if transaction.meter_stop < transaction.meter_start:
        logging.critical("Transaction meter_stop meter_start dan kichik bu daxshatli xato to'g'irlash kerak")
        transaction.meter_consumed = 0
    else:
        transaction.meter_consumed = transaction.meter_stop - transaction.meter_start
    transaction.end_date = timezone.now()
    transaction.amount = calc_energy_price(transaction.meter_consumed)
    transaction.is_force_stop = force_stop
    transaction.save()
    ws_transaction_event(transaction, host)
    logging.info("stop transaction charger=%s transaction=%s reason=%s", data.charger, data.transaction_id, data.reason)


def suspend_connectors(charger: ChargerModel, host: str):
    """Charger connectorlarini o'chirish

    Args:
        charger: [TODO:description]
    """
    connectors = charger.connectors.all()
    logging.info("suspending connectors charger=%s", charger)
    for conn in connectors:
        conn.status = ConnectorStatusEnum.SUSPENDED_EV.value
        conn.save()
        transaction = connector_active_transaction(conn)
        if transaction is not None:
            stop_transaction(transaction, TransactionStatusEnum.PENDING, host=host, data=None, force_stop=True)
        ws_connector_event(conn, host)


def connector_active_transaction(conn: ConnectorModel) -> TransactionModel:
    """Connectordagi active trnasaction

    Args:
        conn: [TODO:description]

    Returns:
        [TODO:description]
    """
    transaction = TransactionModel.objects.filter(conn=conn, is_active=True).order_by("-id").first()
    if transaction is None:
        return None
    return transaction


def parse_charger_id(charger: str) -> str:
    """Parse charger id example test.localhost:212 -> 212

    Args:
        charger: [TODO:description]

    Returns:
        37H

    Raises:
        Exception: Invalid charger id
    """
    id_segments = charger.split(":")
    if len(id_segments) != 2:
        raise Exception("Invalid charger id")
    return id_segments[1]


def make_charger_id(host: str, charger: str) -> str:
    """[TODO:summary]

    Args:
        host: [TODO:description]
        charger: [TODO:description]

    Returns:
        [TODO:description]
    """
    return "%s:%s" % (host, charger)
