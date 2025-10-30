# type: ignore
import json
import logging
from typing import Dict, List
import redis
from config.env import env
from core.apps.api.models.transaction import TransactionModel
from random import randrange

from core.apps.api.schemas.events import MeterValueData, SampledValue


client = redis.Redis(host=env.str("REDIS_HOST", "redis"))


def generate_str(length=10):
    chars = "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    tag = "".join([chars[randrange(1, len(chars))] for _ in range(length)])
    if TransactionModel.objects.filter(tag=tag).exists():
        return generate_tag()
    return tag


def generate_tag(length=10):
    return generate_str(length)


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
    meter_values = []
    for item in data:
        sampledValue = {}
        for value in item.sampledValue:
            sampledValue[value.measurand] = value
        meter_values.append(sampledValue)
    return meter_values


def get_meter(data: Dict[str, SampledValue]) -> int:
    value = data["Energy.Active.Import.Register"].value
    if value == "":
        return 0
    return int(value)
