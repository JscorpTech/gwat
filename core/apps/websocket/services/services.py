import logging
from typing import Any
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_event(group: str, data: dict[str, Any]):
    """frontendga eventlarni yuborish

    Args:
        group: ws group
        data: event data
    """
    logging.info("method: send_event event group=%s data=%s", group, data)
    return async_to_sync(get_channel_layer().group_send)(group, {"data": data, "type": "chat_message"})  # type: ignore


def get_group_name(host: str, station) -> str:
    return "charger_events_%s_%s" % (host, station.pk)
