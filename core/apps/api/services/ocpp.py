# type: ignore
from decimal import Decimal
import json
import logging
from typing import Dict, List
from django.utils import timezone
import redis
from config.env import env
from core.apps.api.enums.transaction import TransactionStatusEnum
from core.apps.api.models.transaction import TransactionModel
from random import randrange

from core.apps.api.schemas.events import MeterValueData, SampledValue, StopTransaction
from core.apps.api.services.payment import calc_energy_price
from core.apps.api.services.ws import ws_transaction_event


client = redis.Redis(host=env.str("REDIS_HOST", "redis"))


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


def remote_start_transaction(charger_id: str, conn_id: int, tag: str):
    """
    Args:
        charger_id (str): charger point id
        conn_id (int): connector id
        tag (str):
    Returns:
        None:
    """
    logging.info("Remote command start transaction charger=%s conn=%s tag=%s", charger_id, conn_id, tag)
    logging.info(id(client))
    client.rpush(
        "commands",
        json.dumps(
            {
                "CpId": str(charger_id),
                "data": [
                    2,
                    generate_str(36),
                    "RemoteStartTransaction",
                    {
                        "idTag": tag,
                        "connectorId": conn_id,
                    },
                ],
            }
        ),
    )


def remote_stop_transaction(charger_id: int, transaction_id: int):
    """
    Args:
        charger_id (str): charger point id
        transaction_id (str): transaction id
    Returns:
        None:
    """
    logging.info("Remote command stop transaction charger=%s transaction=%s", charger_id, transaction_id)
    client.rpush(
        "commands",
        json.dumps(
            {
                "CpId": str(charger_id),
                "data": [
                    2,
                    generate_str(36),
                    "RemoteStopTransaction",
                    {
                        "transactionId": transaction_id,
                    },
                ],
            }
        ),
    )


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


def stop_transaction(transaction: TransactionModel, status: TransactionStatusEnum, data: StopTransaction):
    """Transactionni tugatish databaseni yangilaydi va notification yuboradi

    Args:
        transaction: [TODO:description]
        status: [TODO:description]
        data: [TODO:description]
    """
    transaction.status = status.value
    transaction.meter_stop = data.meter_stop
    if transaction.meter_stop < transaction.meter_start:
        logging.critical("Transaction meter_stop meter_start dan kichik bu daxshatli xato to'g'irlash kerak")
        transaction.meter_consumed = 0
    else:
        transaction.meter_consumed = transaction.meter_stop - transaction.meter_start
    transaction.end_date = timezone.now()
    transaction.amount = calc_energy_price(transaction.meter_consumed)
    transaction.save()
    ws_transaction_event(transaction)
    logging.info("stop transaction charger=%s transaction=%s reason=%s", data.charger, data.transaction_id, data.reason)
